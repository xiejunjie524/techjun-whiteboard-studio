#!/usr/bin/env python3
"""科技俊白板工坊：轻量的一键项目入口。"""
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARSE = ROOT / "scripts" / "parse_srt.py"
RENDER = ROOT / "scripts" / "render_stream_whiteboard.py"
PREVIEW = ROOT / "scripts" / "render_annotation_preview.py"
ANNOTATE = ROOT / "scripts" / "auto_annotate.py"
MERGE = ROOT / "scripts" / "merge_scenes.py"
AUTOPILOT = ROOT / "scripts" / "autopilot.py"
HAND = ROOT / "assets" / "drawing-hand-techjun.png"
DEFAULT_CONFIG = ROOT / "config" / "default.json"

def run(cmd: list[str]) -> None:
    print("[run]", " ".join(map(str, cmd)))
    subprocess.run([str(x) for x in cmd], check=True)

def load_config(path: Path | None) -> dict:
    config_path = path or DEFAULT_CONFIG
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"配置文件无效: {config_path} ({exc})")

def require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise SystemExit(f"{label}不存在: {path}")

def init_project(srt: Path, out: Path, config: dict) -> None:
    require_file(srt, "SRT 文件")
    out.mkdir(parents=True, exist_ok=True)
    result = subprocess.run([sys.executable, str(PARSE), str(srt), "--target-sec", str(config.get("sceneTargetSec", 30)), "--min-sec", str(config.get("sceneMinSec", 25)), "--max-sec", str(config.get("sceneMaxSec", 35))], capture_output=True, text=True, check=True)
    (out / "storyboard.json").write_text(result.stdout, encoding="utf-8")
    print(f"已生成分镜草稿: {out / 'storyboard.json'}")

def preview(image: Path, annotation: Path, output: Path) -> None:
    require_file(image, "图片"); require_file(annotation, "标注文件")
    run([sys.executable, PREVIEW, image, annotation, output])

def render(image: Path, annotation: Path, output: Path, config: dict) -> None:
    require_file(image, "图片"); require_file(annotation, "标注文件")
    hand = HAND if HAND.exists() else ROOT / "assets" / "drawing-hand.png"
    run([sys.executable, RENDER, image, annotation, output, hand, "--ink-path", config.get("inkPath", "grid"), "--color-fill", config.get("colorFill", "contour-wipe"), "--cap-long-edge", str(config.get("capLongEdge", 1080)), "--fps", str(config.get("fps", 60))])

def main() -> int:
    p = argparse.ArgumentParser(prog="techjun", description="科技俊品牌 SRT 白板动画工具")
    sub = p.add_subparsers(dest="command", required=True)
    a = sub.add_parser("storyboard"); a.add_argument("srt", type=Path); a.add_argument("--out", type=Path, default=Path("project")); a.add_argument("--config", type=Path)
    a = sub.add_parser("preview"); a.add_argument("image", type=Path); a.add_argument("annotation", type=Path); a.add_argument("output", type=Path)
    a = sub.add_parser("annotate"); a.add_argument("image", type=Path); a.add_argument("cues", type=Path); a.add_argument("output", type=Path)
    a = sub.add_parser("render"); a.add_argument("image", type=Path); a.add_argument("annotation", type=Path); a.add_argument("output", type=Path); a.add_argument("--config", type=Path)
    a = sub.add_parser("autopilot"); a.add_argument("srt", type=Path); a.add_argument("--out", type=Path, default=Path("output-autopilot")); a.add_argument("--config", type=Path); a.add_argument("--resume", action="store_true")
    if len(sys.argv) == 1: p.print_help(); return 0
    args = p.parse_args()
    config = load_config(getattr(args, "config", None))
    if args.command == "autopilot":
        cmd = [sys.executable, AUTOPILOT, args.srt, "--out", args.out, "--config", args.config or DEFAULT_CONFIG]
        if args.resume: cmd.append("--resume")
        run(cmd)
    elif args.command == "storyboard": init_project(args.srt, args.out, config)
    elif args.command == "annotate": run([sys.executable, ANNOTATE, args.image, args.cues, args.output])
    elif args.command == "preview": preview(args.image, args.annotation, args.output)
    elif args.command == "render": render(args.image, args.annotation, args.output, config)
    return 0

if __name__ == "__main__": raise SystemExit(main())
