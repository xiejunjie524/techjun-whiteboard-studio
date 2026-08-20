# 科技俊白板工坊

把 SRT 字幕和无文字插画制作成品牌化白板手绘 MP4。

## 特点

- 字幕驱动的分镜和区域时序
- 流式 `ink → color` 笔迹渲染
- 智画生成图片后可直接接入
- 根据分离式画面自动生成区域标注初稿
- 科技俊品牌笔手素材
- Windows / macOS / Linux 可运行
- 可作为 Codex Skill 使用

## 快速开始

```bash
python scripts/prepare_env.py
python scripts/techjun.py storyboard input.srt --out project
python scripts/techjun.py annotate image.png cues.json image.annotation.json
python scripts/techjun.py render image.png image.annotation.json output.mp4
```

图片与标注必须同名。完整的区域字段格式沿用上游项目的 `annotation.json` 规范。

## GitHub 发布

```bash
git init
git add .
git commit -m "feat: create Tech Jun whiteboard studio"
git branch -M main
git remote add origin https://github.com/<your-account>/techjun-whiteboard-studio.git
git push -u origin main
```

本项目是上游项目的衍生作品。上游版权和 MIT 许可文件已保留；新增代码与品牌素材由本项目作者维护。
