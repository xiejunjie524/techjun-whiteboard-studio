import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from parse_srt import parse_srt
from auto_annotate import find_regions

def test_srt_parser_accepts_comma_and_dot_milliseconds():
    cues = parse_srt("1\n00:00:00,000 --> 00:00:01.500\n你好\n")
    assert cues[0]["endMs"] == 1500

def test_region_count_and_bounds():
    import numpy as np
    mask = np.zeros((100, 300), dtype=np.uint8)
    mask[20:80, 10:80] = 255; mask[20:80, 110:180] = 255; mask[20:80, 210:280] = 255
    regions = find_regions(mask, 3)
    assert len(regions) == 3
    assert all(r["x"] >= 0 and r["x"] + r["width"] <= 300 for r in regions)

def test_example_annotation_is_valid_shape():
    ann = json.loads((ROOT / "examples/scene-01-seed-growth.annotation.json").read_text(encoding="utf-8"))
    assert len(ann["elements"]) == 3
    assert [e["sequence"] for e in ann["elements"]] == [1, 2, 3]
