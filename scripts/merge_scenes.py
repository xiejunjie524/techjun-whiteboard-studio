#!/usr/bin/env python3
"""
多幕合并：把各场景的白板动画 MP4 按顺序硬切拼接成一条完整视频。

优先用系统 ffmpeg 无损拼接（-c copy，不重编码）；各片尺寸/编码不一致或无
ffmpeg 时，回退到 PyAV 逐帧重编码并缩放补边到第一段尺寸。单片仍保留。

用法：
  <ENV_PY> merge_scenes.py --inputs a.mp4 b.mp4 c.mp4 --output final.mp4
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import json
from pathlib import Path


def _ffmpeg_concat_copy(inputs: list[Path], output: Path) -> bool:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        return False
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        for p in inputs:
            f.write(f"file '{p.resolve().as_posix()}'\n")
        list_path = Path(f.name)
    try:
        res = subprocess.run(
            [ffmpeg, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
             "-i", str(list_path), "-c", "copy", str(output)],
            capture_output=True, text=True,
        )
        if res.returncode == 0:
            print(f"  ffmpeg 无损拼接完成: {output}")
            return True
        print(f"  [warn] ffmpeg -c copy 失败，尝试重编码: {res.stderr.strip()[:200]}")
        res = subprocess.run(
            [ffmpeg, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
             "-i", str(list_path), "-c:v", "libx264", "-crf", "20",
             "-pix_fmt", "yuv420p", "-vf", "scale='trunc(iw/2)*2':'trunc(ih/2)*2'", str(output)],
            capture_output=True, text=True,
        )
        if res.returncode == 0:
            print(f"  ffmpeg 重编码拼接完成: {output}")
            return True
        print(f"  [warn] ffmpeg 重编码也失败: {res.stderr.strip()[:200]}")
        return False
    finally:
        list_path.unlink(missing_ok=True)


def _pyav_concat(inputs: list[Path], output: Path) -> bool:
    try:
        import av
    except ImportError:
        return False
    import numpy as np  # noqa: F401
    first = av.open(str(inputs[0]))
    vs = first.streams.video[0]
    w, h = vs.codec_context.width, vs.codec_context.height
    rate = vs.average_rate
    first.close()

    out = av.open(str(output), mode="w")
    ostream = out.add_stream("h264", rate=rate)
    ostream.width, ostream.height = w, h
    ostream.pix_fmt = "yuv420p"
    ostream.options = {"crf": "24", "preset": "medium"}
    for p in inputs:
        cont = av.open(str(p))
        for frame in cont.decode(video=0):
            if frame.width != w or frame.height != h:
                frame = frame.reformat(width=w, height=h)
            for pkt in ostream.encode(frame):
                out.mux(pkt)
        cont.close()
    for pkt in ostream.encode(None):
        out.mux(pkt)
    out.close()
    print(f"  PyAV 拼接完成: {output}")
    return True


def _ffmpeg_xfade(inputs: list[Path], output: Path, plan_path: Path) -> bool:
    ffmpeg, ffprobe = shutil.which("ffmpeg"), shutil.which("ffprobe")
    if ffmpeg is None or ffprobe is None or not plan_path.exists() or len(inputs) < 2:
        return False
    rows = json.loads(plan_path.read_text(encoding="utf-8")).get("transitions", [])
    if len(rows) != len(inputs) - 1 or any(r.get("style") == "cut" for r in rows):
        return False
    durations = []
    for item in inputs:
        probe = subprocess.run([ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(item)], capture_output=True, text=True)
        if probe.returncode != 0: return False
        durations.append(float(probe.stdout.strip()))
    cmd = [ffmpeg, "-y", "-loglevel", "error"]
    for item in inputs: cmd += ["-i", str(item)]
    filters, current, elapsed = [], "[0:v]", durations[0]
    for i, row in enumerate(rows):
        duration = float(row.get("durationSec", 0.18)); offset = max(0.0, elapsed - duration); out = f"xf{i}"
        filters.append(f"{current}[{i+1}:v]xfade=transition={row.get('style', 'fade')}:duration={duration}:offset={offset}[{out}]")
        current, elapsed = f"[{out}]", elapsed + durations[i + 1] - duration
    result = subprocess.run(cmd + ["-filter_complex", ";".join(filters), "-map", current, "-an", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", str(output)], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  ffmpeg 自动转场完成: {output}"); return True
    print(f"  [warn] 自动转场失败，回退硬切: {result.stderr.strip()[:240]}"); return False


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="按顺序合并多幕白板动画 MP4")
    p.add_argument("--inputs", nargs="+", required=True, help="按播放顺序的 MP4 列表")
    p.add_argument("--output", required=True, help="合并输出路径")
    p.add_argument("--transition-plan", help="transition_director.py 生成的 JSON 计划")
    args = p.parse_args(argv)

    inputs = [Path(x) for x in args.inputs]
    missing = [str(x) for x in inputs if not x.exists()]
    if missing:
        print(f"[err] 缺少输入文件: {', '.join(missing)}", file=sys.stderr)
        return 1
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    plan = Path(args.transition_plan) if args.transition_plan else None
    if (plan and _ffmpeg_xfade(inputs, output, plan)) or _ffmpeg_concat_copy(inputs, output) or _pyav_concat(inputs, output):
        print(f"OUTPUT={output.resolve()}")
        return 0
    print("[err] 合并失败：系统无 ffmpeg 且 PyAV 不可用", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
