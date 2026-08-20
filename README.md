# 科技俊白板工坊

中文 | [English](README.en.md)

把 SRT 字幕、无文字插画和品牌笔手制作成流式白板手绘 MP4，适合知识科普、故事口播、课程短视频和系列化日更内容。

## 示例视频

[下载/播放示例视频](examples/scene-01-seed-growth-whiteboard.mp4)

示例主题：种子落入土里 -> 雨水让它发芽 -> 长成向阳植物。

![标注预览](examples/scene-01-seed-growth-preview.png)

## 功能

- SRT 字幕解析和场景分镜草稿
- `ink -> color` 流式笔迹渲染
- 分离式插画自动生成标注初稿
- 区域、顺序、时序和遮挡保护区控制
- 科技俊品牌笔手素材
- Windows、macOS、Linux 支持
- 可作为 Codex Skill 使用

## 快速开始

```bash
python scripts/prepare_env.py
python scripts/techjun.py storyboard examples/seed-growth.srt --out project
python scripts/techjun.py annotate image.png examples/cues.json image.annotation.json
python scripts/techjun.py preview image.png image.annotation.json image-preview.png
python scripts/techjun.py render image.png image.annotation.json output.mp4
```

图片与标注必须同名。智画生成的源图应遵循：暖米黄纸张、深灰线稿、少量概念色、画面无文字。

## 许可证与来源

本项目是 [geeklee/srt-whiteboard-animation](https://github.com/geeklee/srt-whiteboard-animation) 的独立二创版本，保留上游 MIT 许可和来源声明；新增代码、配置和“科技俊”品牌素材由本项目维护。详见 [LICENSE](LICENSE)。
