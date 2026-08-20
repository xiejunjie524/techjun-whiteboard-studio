import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from parse_srt import parse_srt
from auto_annotate import find_regions
from autopilot import distribute, make_beats

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

def test_autopilot_beat_distribution_preserves_order():
    cues = [{"text": str(i), "startMs": i*1000, "endMs": (i+1)*1000} for i in range(5)]
    beats = make_beats(cues, 3, 0)
    assert len(beats) == 3
    assert "0" in beats[0]["text"] and "4" in beats[-1]["text"]
    assert beats[0]["startMs"] == 0 and beats[-1]["endMs"] == 5000
