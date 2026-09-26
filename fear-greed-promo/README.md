# Fear & Greed Graph — Every Angle

Original 15-second, 1920×1080, 60 fps product motion graphic. The MP4 is generated locally into `renders/fear-greed-graph-15s.mp4` and intentionally excluded from Git. All interfaces are real screenshots from fearandgreedgraph.com captured at 2× density; no market readings or AI responses were authored for the animation.

## Reproduce

Requires Node 22+, Python with NumPy, FFmpeg, and Chrome.

```powershell
npm ci
python scripts/make-audio.py
node scripts/build.mjs
npm run check
npm run render -- --fps 60 --quality delivery --output renders/fear-greed-graph-15s.mp4
```

Run `npx hyperframes@0.8.78 preview --background` for the editable Studio timeline. The seven clips follow `STORYBOARD.md`; revise composition styles and choreography in `scripts/build.mjs`, then rebuild.

## Assets and provenance

- `assets/gauge-close.png`, `compare-*.png`: real homepage gauge, SPY to NVIDIA selection, then six-month range.
- `assets/maps.png`: real Stock Maps screenshot.
- `assets/screener-filter.png`, `screener-result.png`: real market-cap filter and returned results.
- `assets/holdings-table.png`: actual Citadel Advisors holdings from the site's 13F page.
- `assets/stock-save.png`, `save-signin.png`: real NVIDIA page before and after Add to watchlist. The signed-out message is shown; successful saving is not simulated. This treatment was chosen by the user.
- `assets/lilo.png`: actual Lilo question and response, with the site's Graph Comparison link.
- `assets/brand-mark.png`, `geist.woff2`, `geist-mono.woff2`: site's logo and font files. Geist is licensed under SIL OFL; see `assets/OFL.txt`.
- `assets/soundtrack.wav`: original 120 BPM stereo electronic cue synthesized by `scripts/make-audio.py`. No external music samples or reference audio used.
- `assets/gsap.min.js`: vendored GSAP 3.15.0 runtime; see `assets/GSAP-LICENSE.txt`.

The reference MP4 guided pacing, color changes, geometric motion, and typography. No reference footage, music, wordmark, or icon was included.

Capture scripts are reproducible but depend on live UI and data. Keep the checked-in capture files for this exact edit. Refreshing them changes the visual content and requires a new review.

## Verification

HyperFrames checks the runtime, layout and text contrast. Final encoding is inspected with FFprobe for 900 frames, 1920×1080, 60/1 fps, and 15.000 seconds. The last second holds the brand, tagline and address steady. Organizational lint warnings recommend sub-compositions; the seven scenes are intentionally kept in one short, editable timeline.
