# API Reference

## Content Server

### `generate_blog_post`
生成高质量的博客文章内容。

**参数:**
- `topic` (string): 博客主题
- `style` (string, optional): 写作风格 (academic, casual, technical)
- `length` (string, optional): 文章长度 (short, medium, long)
- `language` (string, optional): 语言 (zh-cn, en)

**返回:**
- 完整的 Markdown 格式博客文章

### `optimize_content`
优化现有内容的 SEO 和可读性。

**参数:**
- `content` (string): 原始内容
- `target_keywords` (array): 目标关键词列表

**返回:**
- 优化后的内容

---

## Guesthouse Server

### `design_guesthouse`
基于纳西文化设计民宿方案。

**参数:**
- `style` (string): 设计风格 (traditional, modern, fusion)
- `budget` (number): 预算范围
- `rooms` (number): 房间数量
- `location` (string): 位置描述

**返回:**
- 详细的设计方案和文化元素说明

### `generate_renovation_plan`
生成装修改造计划。

**参数:**
- `current_state` (string): 当前状态描述
- `target_style` (string): 目标风格
- `budget` (number): 预算

**返回:**
- 分阶段的装修计划

---

## Media Server

### `generate_image`
生成图像内容。

**参数:**
- `prompt` (string): 图像描述
- `style` (string, optional): 图像风格
- `size` (string, optional): 图像尺寸

**返回:**
- 图像生成结果

### `create_video_script`
创建视频脚本。

**参数:**
- `topic` (string): 视频主题
- `duration` (number): 视频时长（秒）
- `style` (string): 视频风格

**返回:**
- 详细的视频脚本

---

## Management Server

### `analyze_blog_performance`
分析博客性能指标。

**参数:**
- `blog_path` (string): 博客路径
- `metrics` (array): 要分析的指标

**返回:**
- 性能分析报告

### `generate_content_calendar`
生成内容日历。

**参数:**
- `theme` (string): 主题
- `duration_days` (number): 持续天数
- `post_frequency` (number): 发布频率

**返回:**
- 详细的内容日历

### `optimize_seo`
优化 SEO 配置。

**参数:**
- `content` (string): 内容
- `target_keywords` (array): 目标关键词

**返回:**
- SEO 优化建议
