# Musique « curieuse » en boucle parfaite de 8 s (4 mesures à 120 bpm), composée ici, sans droits.
# Tout est écrit dans un tampon circulaire : les queues de notes et l'écho repartent au début.
import numpy as np, wave, sys
SR = 44100; T = 8.0; N = int(SR * T); L = np.zeros(N); R = np.zeros(N)
def put(sig, at, pan=0.0, g=1.0):
    i = int(round(at * SR)) % N; idx = (i + np.arange(len(sig))) % N
    np.add.at(L, idx, sig * g * (1 - max(0, pan))); np.add.at(R, idx, sig * g * (1 + min(0, pan)))
def pluck(f, d=0.35, br=1.0):
    x = np.arange(int(SR * d)) / SR; env = np.exp(-x * 14) * (1 - np.exp(-x * 900))
    return env * (np.sin(2*np.pi*f*x) + 0.35*br*np.sin(4*np.pi*f*x) + 0.12*br*np.sin(6*np.pi*f*x))
rng = np.random.default_rng(1)
def tick(g):
    x = np.arange(int(SR * 0.03)) / SR; return rng.standard_normal(len(x)) * np.exp(-x * 260) * g
n = lambda m: 440 * 2 ** ((m - 69) / 12)
e = 0.25  # croche à 120 bpm
motif = [62, None, 65, 62, 69, None, 68, None, 62, None, 65, 62, 70, 69, 68, None,
         62, None, 65, 62, 69, None, 68, None, 74, None, 73, None, 70, 69, 68, 65]
for j, m in enumerate(motif):
    if m: put(pluck(n(m)), j * e, pan=(-0.3 if j % 2 else 0.3), g=0.30)
for j in range(16):                       # basse pizz sur chaque temps
    put(pluck(n(38 if j % 8 < 6 else 41), 0.5, 0.4), j * 0.5, g=0.42)
for j in range(32):                       # tic-tac
    put(tick(0.45 if j % 2 == 0 else 0.25), j * e, pan=0.5 if j % 2 else -0.5)
x = np.arange(int(SR * 1.6)) / SR         # impact grave sur le 1er temps des mesures 1 et 3
boom = np.sin(2*np.pi*(45 + 60*np.exp(-x*18))*x) * np.exp(-x*2.2) * 0.7
for at in (0.0, 4.0): put(boom, at)
x = np.arange(int(SR * 8)) / SR           # nappe tenue continue (période 8 s)
pad = sum(np.sin(2*np.pi*n(m)*x) for m in [50, 57, 62, 65]) * 0.035
L += pad; R += pad
for d, g in [(0.25, 0.3), (0.5, 0.15)]:   # écho circulaire
    s = int(d * SR); L, R = L + np.roll(R, s) * g, R + np.roll(L, s) * g
m = max(np.abs(L).max(), np.abs(R).max()); L, R = L / m * 0.89, R / m * 0.89
st = (np.stack([L, R], 1) * 32767).astype(np.int16)
w = wave.open(sys.argv[1], 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes()); w.close()
