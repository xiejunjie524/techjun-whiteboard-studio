#!/usr/bin/env python3
"""无人值守流水线：SRT -> 智画插画 -> 自动标注 -> 校验 -> MP4 -> 合并。"""
from __future__ import annotations
import argparse, base64, json, os, subprocess, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARSE = ROOT / "scripts/parse_srt.py"
ANNOTATE = ROOT / "scripts/auto_annotate.py"
VALIDATE = ROOT / "scripts/validate_project.py"
RENDER = ROOT / "scripts/render_stream_whiteboard.py"
MERGE = ROOT / "scripts/merge_scenes.py"
TRANSITIONS = ROOT / "scripts/transition_director.py"
HAND = ROOT / "assets/drawing-hand-techjun.png"

def run(cmd: list[object], capture: bool = False) -> str:
    result = subprocess.run([str(x) for x in cmd], text=True, capture_output=capture, check=True)
    return result.stdout if capture else ""

def load_wisart() -> tuple[str, str]:
    key = os.getenv("WISART_API_KEY", "").strip()
    url = os.getenv("WISART_BASE_URL", "https://wisart.kuaileshifu.com").rstrip("/")
    env_file = Path.home() / ".codex/wisart.env"
    if env_file.exists() and not key:
        for line in env_file.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.strip().startswith("WISART_API_KEY="): key = line.split("=", 1)[1].strip().strip('"\'')
            if line.strip().startswith("WISART_BASE_URL="): url = line.split("=", 1)[1].strip().strip('"\'').rstrip("/")
    if not key: raise SystemExit("缺少 WISART_API_KEY；请设置环境变量或 ~/.codex/wisart.env")
    return key, url

def wisart_generate(prompt: str, output: Path, model: str, size: str, retries: int) -> None:
    key, base = load_wisart()
    payload = json.dumps({"model": model, "prompt": prompt, "size": size, "quality": "auto", "n": 1, "response_format": "url"}, ensure_ascii=False).encode("utf-8")
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(base + "/v1/images/generations", data=payload, method="POST", headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=600) as response: result = json.load(response)
            item = result["data"][0]
            if item.get("b64_json"): data = base64.b64decode(item["b64_json"])
            else:
                with urllib.request.urlopen(item.get("url") or item["image_url"], timeout=600) as image_response: data = image_response.read()
            output.parent.mkdir(parents=True, exist_ok=True); output.write_bytes(data)
            if output.stat().st_size < 1024: raise RuntimeError("生成图片过小")
            return
        except Exception as exc:
            if attempt == retries: raise RuntimeError(f"智画生成失败，已重试 {retries} 次: {exc}") from exc
            time.sleep(min(2 ** attempt, 10))

def distribute(total: int, groups: int) -> list[tuple[int, int]]:
    return [(round(i * total / groups), round((i + 1) * total / groups)) for i in range(groups)]

def make_beats(cues: list[dict], max_beats: int, scene_start: int) -> list[dict]:
    groups = min(max_beats, len(cues)); beats = []
    for i, (a, b) in enumerate(distribute(len(cues), groups), 1):
        part = cues[a:b]; text = " ".join(x["text"] for x in part)
        beats.append({"label": f"叙事节点{i}", "text": text, "startMs": part[0]["startMs"] - scene_start,
                      "endMs": part[-1]["endMs"] - scene_start, "narrativeRole": "按口播顺序自动生成的叙事节点"})
    return beats

def image_prompt(beats: list[dict], aspect: str) -> str:
    panels = "；".join(f"第{i+1}个独立区域表现：{b['text']}" for i, b in enumerate(beats))
    orientation = "横向" if aspect == "16:9" else "竖向"
    return (f"{aspect} {orientation}白板手绘插画，暖米黄色纸张背景 #F5EBD7，深灰色清晰素描线条，"
            f"把画面分成 {len(beats)} 个互不重叠且留白充足的叙事区域，从左到右或从上到下依次排列。{panels}。"
            "人物和物体使用极简轮廓，少量低饱和橙色、蓝色、绿色点缀，平面二维，统一风格。"
            "画面中绝对不要出现任何文字、汉字、字母、数字、标签、水印、边框、摄影感或3D效果。")

def parse_srt(srt: Path, config: dict) -> dict:
    raw = run([sys.executable, PARSE, srt, "--target-sec", config.get("sceneTargetSec", 30), "--min-sec", config.get("sceneMinSec", 25), "--max-sec", config.get("sceneMaxSec", 35)], True)
    return json.loads(raw)

def main() -> int:
    p = argparse.ArgumentParser(description="科技俊白板工坊无人值守流水线")
    p.add_argument("srt", type=Path); p.add_argument("--out", type=Path, default=Path("output-autopilot"))
    p.add_argument("--config", type=Path, default=ROOT / "config/default.json")
    p.add_argument("--model", default="gpt-image-2"); p.add_argument("--max-beats", type=int, default=3)
    p.add_argument("--retries", type=int, default=3); p.add_argument("--resume", action="store_true")
    p.add_argument("--skip-render", action="store_true", help="仅执行生成、标注和校验，不输出视频")
    p.add_argument("--skip-preview", action="store_true", help="仅执行生成和校验，不输出预览图")
    p.add_argument("--reuse-image", type=Path, help="测试或重跑时为单幕复用已有图片")
    args = p.parse_args()
    if not args.srt.is_file(): raise SystemExit(f"SRT 不存在: {args.srt}")
    config = json.loads(args.config.read_text(encoding="utf-8")); args.out.mkdir(parents=True, exist_ok=True)
    parsed = parse_srt(args.srt, config); cues = parsed["cues"]; manifest = {"source": str(args.srt), "status": "running", "scenes": []}
    parsed_path = args.out / "parsed-scenes.json"; parsed_path.write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8")
    transition_plan = args.out / "transitions.json"
    run([sys.executable, TRANSITIONS, parsed_path, transition_plan, "--mode", config.get("transitionMode", "auto"), "--duration", config.get("transitionDurationSec", 0.18)])
    videos = []
    for scene in parsed["scenes"]:
        index = scene["sceneIndex"]; stem = f"scene-{index:02d}"; scene_dir = args.out / stem; scene_dir.mkdir(exist_ok=True)
        scene_cues = [c for c in cues if scene["cueRange"][0] <= c["index"] <= scene["cueRange"][1]]
        beats = make_beats(scene_cues, args.max_beats, scene["startMs"])
        cues_path = scene_dir / f"{stem}.cues.json"; image = scene_dir / f"{stem}.png"
        annotation = scene_dir / f"{stem}.annotation.json"; preview = scene_dir / f"{stem}-preview.png"; video = scene_dir / f"{stem}.mp4"
        cues_path.write_text(json.dumps(beats, ensure_ascii=False, indent=2), encoding="utf-8")
        if not (args.resume and image.exists()):
            if args.reuse_image:
                if len(parsed["scenes"]) != 1: raise SystemExit("--reuse-image 仅支持单幕测试")
                image.write_bytes(args.reuse_image.read_bytes())
            else: wisart_generate(image_prompt(beats, config.get("aspect", "16:9")), image, args.model, config.get("aspect", "16:9"), args.retries)
        run([sys.executable, ANNOTATE, image, cues_path, annotation])
        run([sys.executable, VALIDATE, image, annotation])
        if not args.skip_preview:
            run([sys.executable, ROOT / "scripts/render_annotation_preview.py", image, annotation, preview])
        if not args.skip_render:
            run([sys.executable, RENDER, image, annotation, video, HAND, "--ink-path", config.get("inkPath", "grid"), "--color-fill", config.get("colorFill", "contour-wipe"), "--cap-long-edge", config.get("capLongEdge", 1080), "--fps", config.get("fps", 60)])
            videos.append(video)
        manifest["scenes"].append({"index": index, "image": str(image), "annotation": str(annotation), "preview": str(preview) if not args.skip_preview else None, "video": str(video) if not args.skip_render else None, "status": "complete"})
        (args.out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    final = args.out / "final.mp4"
    if not args.skip_render:
        if len(videos) == 1: final.write_bytes(videos[0].read_bytes())
        else: run([sys.executable, MERGE, "--inputs", *videos, "--output", final, "--transition-plan", transition_plan])
    manifest["status"] = "complete"; manifest["output"] = str(final)
    (args.out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OUTPUT={(final if not args.skip_render else args.out / 'manifest.json').resolve()}"); return 0

if __name__ == "__main__": raise SystemExit(main())
