#!/usr/bin/env python3
"""检查 annotation.json 的尺寸、坐标和时序不变量。"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from PIL import Image

def main() -> int:
    p = argparse.ArgumentParser(description="验证图片与白板标注")
    p.add_argument("image", type=Path); p.add_argument("annotation", type=Path)
    args = p.parse_args()
    try: image = Image.open(args.image); ann = json.loads(args.annotation.read_text(encoding="utf-8"))
    except Exception as exc: raise SystemExit(f"读取失败: {exc}")
    w, h = image.size; canvas = ann.get("canvas", {})
    if (canvas.get("width"), canvas.get("height")) != (w, h): raise SystemExit(f"canvas 与图片尺寸不一致: {canvas} != {(w,h)}")
    elements = sorted(ann.get("elements", []), key=lambda x: x.get("sequence", 0))
    if not elements: raise SystemExit("标注没有 elements")
    previous = -1
    for i, el in enumerate(elements, 1):
        if el.get("sequence") != i: raise SystemExit("sequence 必须从 1 连续编号")
        r = el.get("region", {}); x, y, rw, rh = (r.get(k) for k in ("x", "y", "width", "height"))
        if not all(isinstance(v, int) for v in (x,y,rw,rh)) or rw <= 0 or rh <= 0 or x < 0 or y < 0 or x+rw > w or y+rh > h: raise SystemExit(f"区域越界或无效: {el.get('id')}")
        reveal = el.get("reveal", {}); start = reveal.get("startMs", -1); duration = reveal.get("durationMs", 0)
        if start < previous or duration <= 0: raise SystemExit(f"时序无效: {el.get('id')}")
        previous = start
    print(f"VALID scene={ann.get('sceneId','')} elements={len(elements)} canvas={w}x{h}")
    return 0
if __name__ == "__main__": raise SystemExit(main())
