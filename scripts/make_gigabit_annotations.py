import json, re, subprocess, sys
from pathlib import Path
root = Path(__file__).resolve().parents[1] / 'examples/gigabit-300mbps/rendered'
srt = Path(__file__).resolve().parents[1] / 'examples/gigabit-300mbps/narration.srt'
text = srt.read_text(encoding='utf-8-sig')
blocks = re.split(r'\n\s*\n', text.strip())
all_cues = []
all_scenes = []
for i, block in enumerate(blocks, 1):
    lines = block.splitlines(); times = lines[1].replace(',', ':').split(' --> ')
    def ms(t):
        h,m,s,ms = map(int,t.split(':')); return ((h*60+m)*60+s)*1000+ms
    start, end = ms(times[0]), ms(times[1])
    cue = {'index': i, 'startMs': 0, 'endMs': end - start, 'text': ' '.join(lines[2:])}
    all_cues.append({'index': i, 'startMs': start, 'endMs': end, 'durMs': end-start, 'text': cue['text']})
    all_scenes.append({'sceneIndex': i, 'startMs': start, 'endMs': end, 'sceneDurationMs': end-start, 'cueRange': [i, i], 'text': cue['text']})
    p = root / f'scene-{i:02d}'; p.mkdir(exist_ok=True)
    (p/f'scene-{i:02d}.cues.json').write_text(json.dumps([cue], ensure_ascii=False, indent=2), encoding='utf-8')
    subprocess.run([sys.executable, str(Path(__file__).parent/'auto_annotate.py'), p/f'scene-{i:02d}.png', p/f'scene-{i:02d}.cues.json', p/f'scene-{i:02d}.annotation.json'], check=True)
    subprocess.run([sys.executable, str(Path(__file__).parent/'validate_project.py'), p/f'scene-{i:02d}.png', p/f'scene-{i:02d}.annotation.json'], check=True)
(root/'parsed-scenes.json').write_text(json.dumps({'cues': all_cues, 'scenes': all_scenes}, ensure_ascii=False, indent=2), encoding='utf-8')
