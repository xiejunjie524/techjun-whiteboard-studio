---
name: techjun-whiteboard-studio
description: 将 SRT 字幕、智画插画和科技俊品牌笔手制作成中文白板手绘动画视频。用于知识科普、故事口播、课程短视频、天涯神贴改编，以及需要 SRT→分镜→标注→MP4 流程的任务。
---

# 科技俊白板工坊

这是基于 `geeklee/srt-whiteboard-animation` 的独立二创项目。保留原项目的 MIT 许可、流式笔迹渲染和 `annotation.json` 编排，同时增加统一配置、科技俊品牌素材和一键命令入口。

## 工作流

1. 用 `scripts/techjun.py storyboard input.srt --out project` 解析字幕并生成分镜草稿。
2. 使用智画生成 16:9 或 9:16 的无文字线稿图，放到项目目录。
3. 对分离式横向构图先用 `scripts/techjun.py annotate image.png cues.json image.annotation.json` 生成标注初稿，再按字幕事件修正区域、时间和保护区。
4. 用 `scripts/techjun.py preview` 生成区域检查图。
5. 用户确认标注后，用 `scripts/techjun.py render` 生成 MP4。

## 品牌规范

- 背景使用暖米黄 `#F5EBD7`。
- 线条为深灰素描线，红、橙、蓝、绿色只做少量概念点缀。
- 场景图不放文字、字母、数字或标签。
- 默认使用 `assets/drawing-hand-techjun.png`；不存在时回退到原始手部素材。
- 精修模式逐步确认；日更模式可在外层 Agent 中一次授权后批量执行。

## 命令

```bash
python scripts/prepare_env.py
python scripts/techjun.py storyboard demo.srt --out project
python scripts/techjun.py preview scene.png scene.annotation.json scene-preview.png
python scripts/techjun.py render scene.png scene.annotation.json scene-whiteboard.mp4 --cap 1080
```

原始渲染器、预览台和合并脚本来自 `geeklee/srt-whiteboard-animation`，详见 `LICENSE` 和仓库 README 的来源说明。
