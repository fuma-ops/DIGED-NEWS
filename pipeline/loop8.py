"""Short « titre seul » de 8 s, une seule page, en boucle parfaite, sans voix (format validé le 25/11/2026).
Usage : /usr/bin/python3 pipeline/loop8.py shorts/<dossier>   (lit spec.json)
spec.json : {"tag": "BREAKING", "credit": "...", "bg": "px/123.mp4", "photo": "face.jpg" | null,
  "lines": [["s", "texte"], ["big", "9,700 LBS"], ["sep"], ["who", "Aaron<br>Rodgers"], ["stamp", "Benched."], ["end", "…"]],
  "output": "diged-xxx.mp4"}   — <span class=y>…</span> met un mot en jaune."""
import sys, json, os, subprocess, shutil
d = os.path.abspath(sys.argv[1]); P = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(P)
S = json.load(open(f'{d}/spec.json'))
body = []
for ln in S['lines']:
    k = ln[0]
    if k == 'sep': body.append('<div class="sep"></div>')
    elif k == 'who':
        ph = f'<div class="ph" style="background-image:url({S["photo"]})"></div>' if S.get('photo') else ''
        body.append(f'<div class="who">{ph}<div class="name">{ln[1]}</div></div>')
    else: body.append(f'<div class="{k}">{ln[1]}</div>')
html = open(f'{R}/templates/loop8.html').read().replace('__TAG__', S.get('tag', 'BREAKING')).replace('__BODY__', '\n'.join(body)).replace('__CREDIT__', S.get('credit', ''))
open(f'{d}/loop.html', 'w').write(html)
shot = f"""const {{ chromium }} = require('playwright'); const path = require('path');
const [, , from, to, dir] = process.argv;
(async () => {{ const b = await chromium.launch(); const p = await b.newPage({{ viewport: {{ width: 1080, height: 1920 }} }});
  await p.goto('file://' + path.join(dir, 'loop.html'), {{ waitUntil: 'networkidle' }}); await p.evaluate(() => document.fonts.ready);
  for (let f = +from; f < +to; f++) {{ await p.evaluate((t) => window.render(t), f / 30); await p.screenshot({{ path: path.join(dir, 'lf', `f${{String(f).padStart(5, '0')}}.png`), omitBackground: true }}); }}
  await b.close(); }})();"""
open(f'{d}/lshot.cjs', 'w').write(shot)
shutil.rmtree(f'{d}/lf', ignore_errors=True); os.makedirs(f'{d}/lf')
ps = [subprocess.Popen(['node', f'{d}/lshot.cjs', str(i * 60), str(i * 60 + 60), d]) for i in range(4)]
assert all(p.wait() == 0 for p in ps)
# Fond : un clip, ou une suite [[fichier, début, durée], ...] (durées = 8 s au total) enchaînée en fondus,
# la fin se fondant dans le début pour une boucle sans raccord.
X = 0.6; VF = 'fps=30,scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,eq=brightness=-0.06,setsar=1,format=yuv420p'
bgs = S['bg'] if isinstance(S['bg'], list) else [[S['bg'], 1.0, 8.0]]
assert abs(sum(b[2] for b in bgs) - 8) < 0.01, 'les durées du fond doivent faire 8 s'
if len(bgs) == 1:
    src, a, _ = bgs[0]
    parts = [(src, a + X, 8.0 - X)] ; closing = (src, a, X)
else:
    parts = [(bgs[0][0], bgs[0][1] + X, bgs[0][2])] + [(f, a, du + X) for f, a, du in bgs[1:]]; closing = (bgs[0][0], bgs[0][1], X)
segs = parts + [closing]
ins, f = [], []
for i, (src, a, L) in enumerate(segs):
    ins += ['-stream_loop', '2', '-i', os.path.join(d, src)]
    f.append(f'[{i}:v]trim={a:.3f}:{a + L:.3f},setpts=PTS-STARTPTS,{VF}[s{i}]')
prev, length = 's0', segs[0][2]
for i in range(1, len(segs)):
    off = length - X; f.append(f'[{prev}][s{i}]xfade=transition=fade:duration={X}:offset={off:.3f}[x{i}]'); prev = f'x{i}'; length = off + segs[i][2]
f.append(f'[{prev}]trim=0:8,setpts=PTS-STARTPTS[v]')
subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', ';'.join(f), '-map', '[v]', '-c:v', 'libx264', '-crf', '14', '-preset', 'fast', f'{d}/bgloop.mp4'], check=True)
subprocess.run(['/usr/bin/python3', f'{P}/music_loop.py', f'{d}/music-loop.wav'], check=True)
out = f"{d}/{S.get('output', 'loop8.mp4')}"
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{d}/bgloop.mp4', '-framerate', '30', '-i', f'{d}/lf/f%05d.png', '-i', f'{d}/music-loop.wav',
  '-filter_complex', '[0:v][1:v]overlay=0:0,format=yuv420p,trim=0:8[v]', '-map', '[v]', '-map', '2:a', '-t', '8',
  '-c:v', 'libx264', '-preset', 'slow', '-crf', '21', '-maxrate', '3800k', '-bufsize', '7600k', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', out], check=True)
shutil.rmtree(f'{d}/lf'); os.remove(f'{d}/bgloop.mp4')
print('OK', out, os.path.getsize(out) // 1024, 'Ko')
