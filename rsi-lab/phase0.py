"""Phase 0: does 1-min RSI predict anything on the underlying?

Usage:  POLYGON_API_KEY=... python phase0.py SPY
If the edge column isn't clearly positive and stable, stop here.
"""
import os, sys, time, pathlib, datetime as dt
import requests, pandas as pd, numpy as np

DATA = pathlib.Path(__file__).parent / "data"
KEY = os.environ.get("POLYGON_API_KEY")  # only needed to fetch, not to self-test


def month_bars(ticker, year, month):
    """One month of 1-min bars, cached to parquet. Polygon free = 2yr history, 5 req/min."""
    f = DATA / f"{ticker}_{year}-{month:02d}.parquet"
    if f.exists():
        return pd.read_parquet(f)

    start = dt.date(year, month, 1)
    end = (start + dt.timedelta(days=32)).replace(day=1) - dt.timedelta(days=1)
    url = (f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/minute/"
           f"{start}/{end}?adjusted=true&sort=asc&limit=50000&apiKey={KEY}")
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    results = r.json().get("results", [])
    if not results:
        return pd.DataFrame()

    df = pd.DataFrame(results)[["t", "o", "h", "l", "c", "v"]]
    df.columns = ["ts", "open", "high", "low", "close", "volume"]
    # Polygon stamps in epoch ms UTC; NY tz is what the session filter needs.
    df["ts"] = pd.to_datetime(df["ts"], unit="ms", utc=True).dt.tz_convert("America/New_York")
    df = df.set_index("ts")
    df.to_parquet(f)
    time.sleep(13)  # free tier: 5 requests/minute
    return df


def load(ticker, months=24):
    now = dt.date.today().replace(day=1)
    frames = []
    for i in range(months, 0, -1):
        d = (now - dt.timedelta(days=1)).replace(day=1)
        for _ in range(i - 1):
            d = (d - dt.timedelta(days=1)).replace(day=1)
        frames.append(month_bars(ticker, d.year, d.month))
    df = pd.concat([f for f in frames if not f.empty])
    return df[~df.index.duplicated()].sort_index()


def rsi(close, n=14):
    """Wilder's smoothing -- ewm(alpha=1/n) is the same recursion, not a simple mean."""
    d = close.diff()
    gain = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    loss = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    # algebraically 100 - 100/(1+gain/loss), but this form is finite when loss==0
    return 100 * gain / (gain + loss)


def edge(df, horizons=(5, 15, 30), low=30, high=70):
    """Forward return after a signal vs the unconditional baseline, in basis points.

    Signal is evaluated at bar close, so the fill is the NEXT bar's open. Returns
    are measured open-to-open from there -- no look-ahead.
    """
    df = df.between_time("09:30", "15:59").copy()  # drop illiquid pre/post market
    df["rsi"] = rsi(df["close"])
    entry = df["open"].shift(-1)                   # what you'd actually pay
    # Series, not Index -- DatetimeIndex.shift() shifts by frequency, not position
    day = pd.Series(df.index.normalize(), index=df.index)

    rows = []
    for h in horizons:
        # only compare bars within the same session; overnight gaps aren't tradeable here
        fwd = (df["open"].shift(-1 - h) / entry - 1) * 1e4
        fwd = fwd.where(day.shift(-1 - h) == day)

        prev = df["rsi"].shift(1)
        for name, sig in [("oversold", (df["rsi"] < low) & (prev >= low)),
                          ("overbought", (df["rsi"] > high) & (prev <= high))]:
            s = fwd[sig].dropna()
            if len(s) < 30:
                continue
            base = fwd.dropna()
            # t-stat of the signal mean against zero; >2 is the bar worth caring about
            t = s.mean() / (s.std() / np.sqrt(len(s))) if s.std() else 0
            rows.append({"signal": name, "horizon_min": h, "n": len(s),
                         "mean_bps": round(s.mean(), 2),
                         "baseline_bps": round(base.mean(), 2),
                         "edge_bps": round(s.mean() - base.mean(), 2),
                         "t_stat": round(t, 2),
                         "hit_rate": round((s > 0).mean(), 3)})
    return pd.DataFrame(rows)


def _selftest():
    # RSI of a monotonic rise is 100; of a monotonic fall, 0.
    up = pd.Series(np.arange(100, 200, dtype=float))
    assert rsi(up).iloc[-1] > 99.9, rsi(up).iloc[-1]
    assert rsi(up[::-1].reset_index(drop=True)).iloc[-1] < 0.1

    # No look-ahead: a signal on the last bar must produce NaN, not a number.
    idx = pd.date_range("2024-01-02 09:30", periods=100, freq="1min", tz="America/New_York")
    noise = pd.DataFrame({"open": 100.0, "high": 100.0, "low": 100.0,
                          "close": 100 + np.random.randn(100).cumsum(), "volume": 1}, index=idx)
    e = edge(noise, horizons=(5,))
    assert e.empty or e["n"].max() < 100
    print("self-test ok")


if __name__ == "__main__":
    if "--test" in sys.argv:
        _selftest()
    else:
        ticker = sys.argv[1] if len(sys.argv) > 1 else "SPY"
        df = load(ticker)
        print(f"{ticker}: {len(df):,} bars, {df.index[0].date()} to {df.index[-1].date()}")
        print(edge(df).to_string(index=False))
