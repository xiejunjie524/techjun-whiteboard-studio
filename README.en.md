# Tech Jun Whiteboard Studio

[中文 README](README.md) | English

Turn SRT subtitles, text-free illustrations, and a branded drawing hand into stream-style whiteboard animation MP4 files. It is designed for explainers, narrated stories, lessons, and repeatable short-video production.

## Demo video

[Download / play the demo video](examples/scene-01-seed-growth-whiteboard.mp4)

Demo story: a seed falls into soil -> rain makes it sprout -> it grows toward the sun.

![Annotation preview](examples/scene-01-seed-growth-preview.png)

## Features

- SRT parsing and storyboard drafts
- Stream-style `ink -> color` rendering
- Automatic first-pass annotation for separated illustrations
- Region, order, timing, and protected-region control
- Tech Jun branded drawing-hand asset
- Windows, macOS, and Linux support
- Codex Skill compatible

## Quick start

```bash
python scripts/prepare_env.py
python scripts/techjun.py storyboard examples/seed-growth.srt --out project --config config/default.json
python scripts/techjun.py annotate image.png examples/cues.json image.annotation.json
python scripts/techjun.py preview image.png image.annotation.json image-preview.png
python scripts/validate_project.py image.png image.annotation.json
python scripts/techjun.py render image.png image.annotation.json output.mp4 --config config/default.json
```

## Unattended mode

After configuring `WISART_API_KEY`, one command generates images, annotations, validation previews, scene videos, and the merged result:

```bash
python scripts/techjun.py autopilot input.srt --out output-autopilot --config config/default.json
```

Resume an interrupted run with `--resume`. The final file is written to `output-autopilot/final.mp4`, while `manifest.json` records scene status and artifact paths.

## License and attribution

This is an independent derivative of [geeklee/srt-whiteboard-animation](https://github.com/geeklee/srt-whiteboard-animation). The upstream MIT license and attribution are preserved; new code, configuration, and Tech Jun brand assets are maintained by this project. See [LICENSE](LICENSE).
