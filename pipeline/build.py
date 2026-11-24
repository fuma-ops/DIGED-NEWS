"""Montage complet d'un Short à partir de shorts/<slug>/short.json :
{"segments": [["<fichier mp4 de fond>", début, fin], ...], "duration": 46.4}
Étapes : images de l'habillage (ov.html + caps.json), fonds verticaux enchaînés, voix + musique, MP4 final.
Usage : /usr/bin/python3 pipeline/build.py shorts/<slug>"""
import sys, json, subprocess, os, shutil, math
d = sys.argv[1]; cfg = json.load(open(f'{d}/short.json')); P = os.path.dirname(os.path.abspath(__file__))
T = cfg['duration']; N = math.ceil(T * 30) + 5
# 1) habillage : caps.json injecté dans ov.html, rendu image par image (4 navigateurs en parallèle)
html = open(f'{d}/ov.html').read()
if '__CAPS__' in html: open(f'{d}/ov.html', 'w').write(html.replace('__CAPS__', open(f'{d}/caps.json').read()))
shutil.rmtree(f'{d}/frames', ignore_errors=True)
q = N // 4 + 1
procs = [subprocess.Popen(['node', f'{P}/ovshot.cjs', str(i*q), str(min(N, (i+1)*q)), '30', 'frames', os.path.abspath(d)]) for i in range(4)]
assert all(p.wait() == 0 for p in procs), 'rendu habillage en échec'
# 2) fonds : chaque segment recadré en vertical, léger zoom, fondus enchaînés
X = 0.4; ins, f = [], []
for i, (src, a, b) in enumerate(cfg['segments']):
    L = b - a + X; ins += ['-stream_loop', '-1', '-t', f'{L:.2f}', '-i', src]
    f.append(f"[{i}:v]fps=30,scale=-2:1920:flags=lanczos,crop=1080:1920,zoompan=z='1+0.06*on/{int(L*30)}':d=1:s=1080x1920:fps=30,eq=brightness=-0.08,setsar=1,trim=0:{L:.2f},setpts=PTS-STARTPTS[s{i}]")
prev, off = 's0', 0
for i in range(1, len(cfg['segments'])):
    a, b = cfg['segments'][i-1][1], cfg['segments'][i-1][2]; off += b - a
    f.append(f'[{prev}][s{i}]xfade=transition=fade:duration={X}:offset={off-X/2:.2f}[x{i}]'); prev = f'x{i}'
f.append(f'[{prev}]trim=0:{T},format=yuv420p[v]')
subprocess.run(['ffmpeg','-v','error','-y',*ins,'-filter_complex',';'.join(f),'-map','[v]','-c:v','libx264','-preset','veryfast','-crf','18',f'{d}/bg.mp4'],check=True)
# 3) musique (composée, sans droits) + voix
subprocess.run(['/usr/bin/python3', f'{P}/music.py', str(T + 2), f'{d}/music.wav'], check=True)
out = f"{d}/{cfg.get('output', 'short.mp4')}"
subprocess.run(['ffmpeg','-v','error','-y','-i',f'{d}/bg.mp4','-framerate','30','-i',f'{d}/frames/f%05d.png','-i',f'{d}/vo.mp3','-i',f'{d}/music.wav',
  '-filter_complex',f'[0:v][1:v]overlay=0:0:eof_action=repeat,format=yuv420p[v];[2:a]volume=1.15[vo];[3:a]volume=0.09,afade=t=out:st={T-1.8:.2f}:d=1.8[mu];[vo][mu]amix=inputs=2:duration=first:dropout_transition=0,apad=pad_dur=1[a]',
  '-map','[v]','-map','[a]','-t',str(T),'-c:v','libx264','-preset','medium','-crf','20','-c:a','aac','-b:a','192k','-movflags','+faststart',out],check=True)
shutil.rmtree(f'{d}/frames', ignore_errors=True); os.remove(f'{d}/bg.mp4')
print('OK', out)
