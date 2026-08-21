#!/usr/bin/env python3
"""Choose deterministic transitions from adjacent scene semantics."""
from __future__ import annotations
import argparse, json
from pathlib import Path

def choose(previous: str, current: str, index: int, total: int, mode: str, duration: float) -> dict:
    if mode == "none": style = "cut"
    elif mode == "paper": style = "wipeleft"
    else:
        p, c, text = previous.lower(), current.lower(), (previous + " " + current).lower()
        contrast = (any(k in p for k in ("普通", "聊天机器人", "问答")) and "agent" in c) or any(k in text for k in ("对比", "区别"))
        if contrast: style = "slideright"
        elif any(k in c for k in ("检查", "结果", "重试", "完成", "结论")): style = "fade"
        elif any(k in c for k in ("搜索", "资料", "数据", "代码", "文件", "浏览器", "工具")): style = "wipeleft"
        elif index == total - 2: style = "circlecrop"
        else: style = "fade"
    return {"between": [index, index + 1], "style": style, "durationSec": duration if style != "cut" else 0.0, "reason": "manual mode" if mode != "auto" else "semantic auto-selection", "previousText": previous, "currentText": current}

def main() -> int:
    p = argparse.ArgumentParser(description="Choose whiteboard scene transitions")
    p.add_argument("input", type=Path); p.add_argument("output", type=Path); p.add_argument("--mode", choices=("auto", "none", "paper"), default="auto"); p.add_argument("--duration", type=float, default=0.18)
    args = p.parse_args(); data = json.loads(args.input.read_text(encoding="utf-8")); scenes = data.get("scenes", []); cues = {c["index"]: c for c in data.get("cues", [])}; rows = []
    for i in range(len(scenes) - 1):
        a, b = scenes[i], scenes[i + 1]; at = " ".join(cues[n]["text"] for n in range(a["cueRange"][0], a["cueRange"][1] + 1) if n in cues); bt = " ".join(cues[n]["text"] for n in range(b["cueRange"][0], b["cueRange"][1] + 1) if n in cues); rows.append(choose(at, bt, i, len(scenes), args.mode, args.duration))
    args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(json.dumps({"mode": args.mode, "version": 1, "transitions": rows}, ensure_ascii=False, indent=2), encoding="utf-8"); print(f"OUTPUT={args.output.resolve()}"); return 0

if __name__ == "__main__": raise SystemExit(main())
