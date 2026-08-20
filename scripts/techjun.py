#!/usr/bin/env python3
"""科技俊白板工坊：轻量的一键项目入口。"""
from __future__ import annotations
import argparse, json, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARSE = ROOT / "scripts" / "parse_srt.py"
RENDER = ROOT / "scripts" / "render_stream_whiteboard.py"
PREVIEW = ROOT / "scripts" / "render_annotation_preview.py"
ANNOTATE = ROOT / "scripts" / "auto_annotate.py"
MERGE = ROOT / "scripts" / "merge_scenes.py"
HAND = ROOT / "assets" / "drawing-hand-techjun.png"

def run(cmd: list[str]) -> None:
    print("[run]", " ".join(map(str, cmd)))
    subprocess.run([str(x) for x in cmd], check=True)

def init_project(srt: Path, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    result = subprocess.run([sys.executable, str(PARSE), str(srt), "--target-sec", "30", "--min-sec", "25", "--max-sec", "35"], capture_output=True, text=True, check=True)
    (out / "storyboard.json").write_text(result.stdout, encoding="utf-8")
    print(f"已生成分镜草稿: {out / 'storyboard.json'}")

def preview(image: Path, annotation: Path, output: Path) -> None:
    run([sys.executable, PREVIEW, image, annotation, output])

def render(image: Path, annotation: Path, output: Path, cap: int) -> None:
    hand = HAND if HAND.exists() else ROOT / "assets" / "drawing-hand.png"
    run([sys.executable, RENDER, image, annotation, output, hand, "--ink-path", "grid", "--color-fill", "contour-wipe", "--cap-long-edge", str(cap)])

def main() -> int:
    p = argparse.ArgumentParser(prog="techjun", description="科技俊品牌 SRT 白板动画工具")
    sub = p.add_subparsers(dest="command", required=True)
    a = sub.add_parser("storyboard"); a.add_argument("srt", type=Path); a.add_argument("--out", type=Path, default=Path("project"))
    a = sub.add_parser("preview"); a.add_argument("image", type=Path); a.add_argument("annotation", type=Path); a.add_argument("output", type=Path)
    a = sub.add_parser("annotate"); a.add_argument("image", type=Path); a.add_argument("cues", type=Path); a.add_argument("output", type=Path)
    a = sub.add_parser("render"); a.add_argument("image", type=Path); a.add_argument("annotation", type=Path); a.add_argument("output", type=Path); a.add_argument("--cap", type=int, default=1080)
    if len(sys.argv) == 1: p.print_help(); return 0
    args = p.parse_args()
    if args.command == "storyboard": init_project(args.srt, args.out)
    elif args.command == "annotate": run([sys.executable, ANNOTATE, args.image, args.cues, args.output])
    elif args.command == "preview": preview(args.image, args.annotation, args.output)
    elif args.command == "render": render(args.image, args.annotation, args.output, args.cap)
    return 0

if __name__ == "__main__": raise SystemExit(main())
