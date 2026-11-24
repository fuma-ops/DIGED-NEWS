"""Contrôle de prononciation : retranscrit la vidéo finale avec un AUTRE modèle (medium.en, sans le script)
et compare au script. Usage : /usr/bin/python3 pipeline/check_voice.py <video.mp4> <script.txt>
Critère : >= 97 % des mots retrouvés ; liste les écarts et les mots à faible confiance (< 0.6)."""
import sys, re, difflib, subprocess, numpy as np
from faster_whisper import WhisperModel
v, sc = sys.argv[1], sys.argv[2]
raw = subprocess.run(['ffmpeg','-v','error','-i',v,'-vn','-ar','16000','-ac','1','-f','f32le','-'],capture_output=True,check=True).stdout
a = np.frombuffer(raw, dtype=np.float32)
m = WhisperModel('medium.en', device='cpu', compute_type='int8')
segs, _ = m.transcribe(a, language='en', word_timestamps=True)
words = [w for s in segs for w in s.words]
NUM = set('zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty thirty forty fifty sixty seventy eighty ninety hundred thousand million billion and'.split())
# les nombres s'écrivent en lettres dans le script et en chiffres à la transcription : on les compare à part
norm = lambda s: [w for w in re.sub(r"[^a-z0-9' ]", ' ', s.lower().replace('-', ' ').replace(',', '')).split() if w not in NUM and not w.isdigit()]
ref, hyp = norm(open(sc).read()), norm(' '.join(w.word for w in words))
sm = difflib.SequenceMatcher(a=ref, b=hyp)
ok = sum(b.size for b in sm.get_matching_blocks())
print(f'mots retrouvés : {ok}/{len(ref)} ({100*ok/len(ref):.0f} %)')
for op, i1, i2, j1, j2 in sm.get_opcodes():
    if op != 'equal': print(f'  écart : script « {" ".join(ref[i1:i2])} » / entendu « {" ".join(hyp[j1:j2])} »')
for w in words:
    if w.probability < 0.6: print(f'  confiance faible : {w.word.strip()} ({w.probability:.2f}) à {w.start:.1f}s')
print('débit :', round(len(ref) / (words[-1].end - words[0].start) * 60), 'mots/min (cible 170-200)')
