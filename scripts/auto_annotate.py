#!/usr/bin/env python3
"""根据分离式白板插画的前景分布生成 annotation.json 初稿。"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import cv2
import numpy as np

def foreground_mask(img: np.ndarray) -> np.ndarray:
    h, w = img.shape[:2]
    sample = np.vstack([img[5:35, 5:35].reshape(-1, 3), img[5:35, w-35:w-5].reshape(-1, 3)])
    bg = np.median(sample, axis=0)
    dist = np.linalg.norm(img.astype(np.float32) - bg.astype(np.float32), axis=2)
    mask = (dist > 25).astype(np.uint8) * 255
    return cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))

def find_regions(mask: np.ndarray, count: int) -> list[dict]:
    h, w = mask.shape
    projection = (mask > 0).sum(axis=0)
    active = projection > max(2, int(h * 0.003))
    groups, start = [], None
    for x, on in enumerate(active):
        if on and start is None: start = x
        if start is not None and (not on or x == w - 1):
            end = x if on else x - 1
            if end - start > w * 0.025: groups.append([start, end])
            start = None
    while len(groups) > count:
        gaps = [groups[i+1][0] - groups[i][1] for i in range(len(groups)-1)]
        i = int(np.argmin(gaps)); groups[i:i+2] = [[groups[i][0], groups[i+1][1]]]
    if len(groups) != count:
        groups = [[round(i*w/count), round((i+1)*w/count)-1] for i in range(count)]
    regions = []
    for x0, x1 in groups:
        ys, xs = np.where(mask[:, x0:x1+1] > 0)
        if len(ys): y0, y1 = int(ys.min()), int(ys.max())
        else: y0, y1 = 0, h-1
        pad = 24
        rx, ry = max(0, x0-pad), max(0, y0-pad)
        ex, ey = min(w, x1+pad+1), min(h, y1+pad+1)
        regions.append({"x": rx, "y": ry, "width": ex-rx, "height": ey-ry})
    return regions

def main() -> int:
    p = argparse.ArgumentParser(description="为横向分离式白板图生成标注初稿")
    p.add_argument("image", type=Path)
    p.add_argument("cues", type=Path, help='JSON 数组：[{"text":"...","startMs":0,"endMs":3000}]')
    p.add_argument("output", type=Path)
    args = p.parse_args()
    img = cv2.imdecode(np.fromfile(args.image, dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None: raise SystemExit(f"无法读取图片: {args.image}")
    cues = json.loads(args.cues.read_text(encoding="utf-8"))
    regions = find_regions(foreground_mask(img), len(cues))
    elements = []
    for i, (cue, region) in enumerate(zip(cues, regions), 1):
        start, end = int(cue["startMs"]), int(cue["endMs"])
        elements.append({
            "id": f"element-{i:02d}", "label": cue.get("label", f"叙事元素{i}"),
            "sequence": i, "narrativeRole": cue.get("narrativeRole", "按字幕顺序出现"),
            "subtitle": cue["text"], "type": cue.get("type", "object"), "region": region,
            "reveal": {"direction": "left_to_right", "startMs": start,
                       "durationMs": max(500, end-start), "maskPaddingPx": 18, "protectedRegions": []},
            "handPath": {"start": [region["x"], region["y"] + region["height"]//2],
                         "end": [region["x"]+region["width"], region["y"]+region["height"]//2],
                         "easing": "easeInOut"}
        })
    h, w = img.shape[:2]
    data = {"sceneId": args.image.stem, "canvas": {"width": w, "height": h},
            "storyBasis": " ".join(x["text"] for x in cues),
            "sceneDurationMs": max(x["endMs"] for x in cues) + 500, "elements": elements}
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OUTPUT={args.output.resolve()}")
    return 0

if __name__ == "__main__": raise SystemExit(main())
