#!/usr/bin/env python3
from __future__ import annotations
import argparse, base64, json, os, sys, time, urllib.request
from pathlib import Path

DEFAULT_BASE = "https://test.mlgb7.com/v1"

def load_key() -> str:
    key = os.getenv("MLGB7_API_KEY", "").strip()
    env = Path.home() / ".codex" / "mlgb7.env"
    if not key and env.exists():
        for line in env.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("MLGB7_API_KEY="):
                key = line.split("=", 1)[1].strip().strip("\"'")
    if not key:
        raise SystemExit("缺少 MLGB7_API_KEY；请设置环境变量或 ~/.codex/mlgb7.env")
    return key

def generate(prompt: str, model: str, size: str, out: Path, base: str, retries: int) -> Path:
    key = load_key()
    payload = json.dumps({"model": model, "prompt": prompt, "n": 1, "size": size, "response_format": "url"}, ensure_ascii=False).encode()
    req = urllib.request.Request(base.rstrip("/") + "/images/generations", data=payload, method="POST", headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    last = None
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=600) as resp:
                data = json.load(resp)
            item = data.get("data", [{}])[0]
            if item.get("b64_json"):
                raw = base64.b64decode(item["b64_json"])
            else:
                url = item.get("url") or item.get("image_url")
                if not url: raise RuntimeError("响应没有 b64_json 或 url")
                with urllib.request.urlopen(url, timeout=600) as resp: raw = resp.read()
            if len(raw) < 1024: raise RuntimeError("图片响应过小")
            out.parent.mkdir(parents=True, exist_ok=True); out.write_bytes(raw)
            print(f"OUTPUT={out.resolve()}"); return out
        except Exception as exc:
            last = exc
            if attempt < retries: time.sleep(min(2 ** attempt, 10))
    raise RuntimeError(f"MLGB7 生图失败，已重试 {retries} 次: {last}")

def main() -> int:
    p = argparse.ArgumentParser(description="Generate image through MLGB7 OpenAI-compatible API")
    p.add_argument("--prompt", required=True); p.add_argument("--model", default="gpt-image-2"); p.add_argument("--size", default="1024x1024")
    p.add_argument("--out", type=Path, default=Path("mlgb7-output.png")); p.add_argument("--base-url", default=os.getenv("MLGB7_BASE_URL", DEFAULT_BASE)); p.add_argument("--retries", type=int, default=3)
    a = p.parse_args(); generate(a.prompt, a.model, a.size, a.out, a.base_url, a.retries); return 0
if __name__ == "__main__": raise SystemExit(main())
