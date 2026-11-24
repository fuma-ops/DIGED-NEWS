"""Horodatage mot à mot de la voix off (faster-whisper) -> caps.json pour les sous-titres.
Usage : /usr/bin/python3 pipeline/align.py <dossier_du_short>   (lit vo.mp3 et script.txt)"""
import sys, json, subprocess, numpy as np, os
from faster_whisper import WhisperModel
d = sys.argv[1]
subprocess.run(['ffmpeg','-v','error','-y','-i',f'{d}/vo.mp3','-ar','16000','-ac','1','-f','f32le',f'{d}/vo16.f32'],check=True)
a = np.fromfile(f'{d}/vo16.f32', dtype=np.float32)
m = WhisperModel('small', device='cpu', compute_type='int8')
segs, _ = m.transcribe(a, language='en', word_timestamps=True, initial_prompt=open(f'{d}/script.txt').read())
out = []
for s in segs:
    for w in s.words:
        t = w.word.strip().replace('NARRATOR', '')
        if not t: continue
        # « 224 » + « ,000 » -> « 224,000 » ; « Twenty » + « -two » -> « Twenty-two »
        if out and (t.startswith(',000') or t.startswith('-')):
            out[-1]['w'] += t; out[-1]['e'] = round(w.end, 2); continue
        out.append({'w': t, 's': round(w.start, 2), 'e': round(w.end, 2)})
json.dump(out, open(f'{d}/caps.json', 'w'))
os.remove(f'{d}/vo16.f32')
print(len(out), 'mots ;', ' '.join(x['w'] for x in out))
