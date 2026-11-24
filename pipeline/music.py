import numpy as np, wave
import sys
SR=44100; D=float(sys.argv[1]) if len(sys.argv)>1 else 56.0; N=int(SR*D); t=np.arange(N)/SR; bpm=120; b=60/bpm
out=np.zeros(N)
def env(n,a,d): x=np.arange(n)/SR; return np.minimum(x/a,1)*np.exp(-x/d)
# pulsing bass on eighths (A minor-ish: A, F, C, G per bar)
roots=[55.0,43.65,65.41,49.0]
for k in range(int(D/(b/2))):
    s=int(k*b/2*SR); n=int(0.22*SR); f=roots[(k//8)%4]; x=np.arange(n)/SR
    out[s:s+n]+=0.35*np.sin(2*np.pi*f*x+0.6*np.sin(2*np.pi*f*2*x))*env(n,0.005,0.09)[:len(out[s:s+n])] if s+n<=N else 0
# timpani-like hit each bar + ticking hi-hat on sixteenths
rng=np.random.default_rng(1)
for k in range(int(D/b)):
    s=int(k*b*SR)
    if k%4==0:
        n=int(1.2*SR); x=np.arange(n)/SR; hit=np.sin(2*np.pi*(70*np.exp(-x*1.5))*x)*env(n,0.003,0.35); e=min(N,s+n); out[s:e]+=0.6*hit[:e-s]
for k in range(int(D/(b/4))):
    s=int(k*b/4*SR); n=int(0.03*SR); e=min(N,s+n)
    h=rng.standard_normal(n)*env(n,0.0005,0.008); h=np.diff(np.concatenate([[0],h])); out[s:e]+=(0.12 if k%2 else 0.07)*h[:e-s]
# rising pad
pad=sum(np.sin(2*np.pi*f*t) for f in (220,261.6,329.6))/3*0.08*np.minimum(t/4,1)
out+=pad
out[-int(1.2*SR):]*=np.linspace(1,0,int(1.2*SR))
out=out/np.max(np.abs(out))*0.8
w=wave.open(sys.argv[2] if len(sys.argv)>2 else 'music.wav','wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype(np.int16).tobytes()); w.close()
