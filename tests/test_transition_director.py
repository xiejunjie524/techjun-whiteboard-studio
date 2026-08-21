import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class TransitionDirectorTests(unittest.TestCase):
    def test_auto_selects_semantic_styles(self):
        root = Path(__file__).resolve().parents[1]
        payload = {
            "cues": [
                {"index": 1, "text": "普通聊天机器人回答问题"},
                {"index": 2, "text": "AI Agent 理解目标并调用搜索工具"},
                {"index": 3, "text": "检查结果直到任务完成"},
            ],
            "scenes": [
                {"cueRange": [1, 1]},
                {"cueRange": [2, 2]},
                {"cueRange": [3, 3]},
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "parsed.json"
            target = Path(directory) / "transitions.json"
            source.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            subprocess.run([sys.executable, root / "scripts/transition_director.py", source, target], check=True)
            plan = json.loads(target.read_text(encoding="utf-8"))
        self.assertEqual([row["style"] for row in plan["transitions"]], ["slideright", "fade"])
        self.assertTrue(all(row["durationSec"] == 0.18 for row in plan["transitions"]))

    def test_none_mode_is_cut(self):
        root = Path(__file__).resolve().parents[1]
        payload = {"cues": [], "scenes": [{"cueRange": [1, 1]}, {"cueRange": [2, 2]}]}
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "parsed.json"
            target = Path(directory) / "transitions.json"
            source.write_text(json.dumps(payload), encoding="utf-8")
            subprocess.run([sys.executable, root / "scripts/transition_director.py", source, target, "--mode", "none"], check=True)
            plan = json.loads(target.read_text(encoding="utf-8"))
        self.assertEqual(plan["transitions"][0]["style"], "cut")


if __name__ == "__main__":
    unittest.main()
