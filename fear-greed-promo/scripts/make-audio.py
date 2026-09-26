"""Original 120 BPM electronic cue, synthesized locally; no sampled music."""
from pathlib import Path
import numpy as np
import wave
SR=48000
D=15
rng=np.random.default_rng(260926)
mix=np.zeros((SR*D,2),dtype=np.float64)
def put(start,x,gain=1,pan=0):
    k=round(start*SR);n=min(len(x),len(mix)-k)
    if n<=0:return
    mix[k:k+n,0]+=x[:n]*gain*np.sqrt((1-pan)/2)
    mix[k:k+n,1]+=x[:n]*gain*np.sqrt((1+pan)/2)
def kick(at,gain=.7):
    t=np.arange(int(.38*SR))/SR
    phase=2*np.pi*(48*t+(135-48)*.024*(1-np.exp(-t/.024)))
    x=np.sin(phase)*np.exp(-t*12)+rng.normal(0,.04,len(t))*np.exp(-t*200)
    put(at,x,gain)
def tick(at,gain=.075,pan=0):
    t=np.arange(int(.055*SR))/SR;n=rng.normal(0,1,len(t));n=np.diff(n,prepend=0)
    put(at,n*np.exp(-t*90),gain,pan)
def clap(at):
    t=np.arange(int(.16*SR))/SR;n=rng.normal(0,1,len(t));env=np.exp(-t*25)*(1+np.cos(2*np.pi*70*t))
    put(at,n*env,.085)
def pluck(at,f,gain=.13,pan=0):
    t=np.arange(int(.38*SR))/SR
    x=(np.sin(2*np.pi*f*t)+.25*np.sin(2*np.pi*2*f*t)+.10*np.sin(2*np.pi*3*f*t))*np.exp(-t*13)*(1-np.exp(-t*180))
    put(at,x,gain,pan);put(at+.1875,x,gain*.25,-pan)
for at in [0,.5,1,1.5]:kick(at,.25+at*.15)
for at in np.arange(2,14,.5):kick(at)
for at in np.arange(2.5,14,1):clap(at)
for i,at in enumerate(np.arange(2,14,.125)):tick(at,.034 if i%2 else .058,(-1)**i*.45)
notes=[146.83,220,293.66,349.23,293.66,220,174.61,220]
for i,at in enumerate(np.arange(2,13.75,.25)):pluck(at,notes[i%8],.10,(-1)**i*.35)
for at in [2,3.5,6,8.5,10.5,12.5]:
    kick(at,.85)
    t=np.arange(int(.35*SR))/SR
    put(at,np.sin(2*np.pi*(85*t-60*.13*(1-np.exp(-t/.13))))*np.exp(-t*10),.25)
for at in [4.66,5.28,7.62,10.86,11.30]:tick(at,.17)
for at in [1.68,5.7,8.23,12.2]:
    t=np.arange(int(.3*SR))/SR
    noise=rng.normal(0,1,len(t));low=np.convolve(noise,np.ones(12)/12,mode='same')
    put(at,low*(t/.3)**2,.21)
for f in [146.83,220,293.66]:pluck(13.5,f,.18)
env=np.minimum(1,np.arange(len(mix))/(SR*.012))*np.minimum(1,(len(mix)-np.arange(len(mix)))/(SR*.6))
mix=np.tanh(mix*1.1)*env[:,None]
mix*=.89/max(np.max(np.abs(mix)),1e-9)
out=Path(__file__).resolve().parents[1]/'assets'/'soundtrack.wav'
with wave.open(str(out),'wb') as w:
    w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((mix*32767).astype('<i2').tobytes())
print(f'{out.name}: {D}s, {SR} Hz, stereo; peak {20*np.log10(np.max(np.abs(mix))):.1f} dBFS')
