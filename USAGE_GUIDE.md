# Blog MCP Server 使用指南

## 🎯 系统概述

Blog MCP Server 是一个基于 FastMCP 框架的博客内容创作和客栈管理系统，专为 Polly 的 Zola 博客和丽江客栈项目设计。系统包含四个专业化的 MCP 服务器：

1. **博客内容服务器** (`content_server.py`) - 博文创作、内容优化、格式化
2. **客栈管理服务器** (`guesthouse_server.py`) - 客栈设计、营销文案、文化元素整合
3. **媒体生成服务器** (`media_server.py`) - DALL-E 图片生成、未来 Sora 视频生成
4. **博客管理服务器** (`management_server.py`) - 博客系统管理、文件操作、发布部署

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆或进入项目目录
cd /Users/polly/Downloads/Sublime_Workspace/Zola_Workspace/www.polly.com/Blog_MCP_Server

# 安装依赖
poetry install

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 API 密钥
```

### 2. VS Code 集成

将 `mcp-settings.json` 中的配置添加到你的 VS Code `settings.json`：

```json
{
  "mcp": {
    "mcpServers": {
      // 复制 mcp-settings.json 中的内容到这里
    }
  }
}
```

### 3. 运行测试

```bash
# 运行测试脚本验证所有服务器
./start_test.sh
```

## 🛠️ 功能详解

### 博客内容服务器功能

- **`create_blog_post`** - 创建完整的博文
  - 输入：主题、分类、标签、风格、长度等
  - 输出：完整博文内容、frontmatter、文件路径

- **`optimize_blog_content`** - 优化博文内容
  - 支持 SEO、可读性、参与度优化
  - 提供改进建议和评分

- **`generate_blog_outline`** - 生成博文大纲
  - 支持不同深度的大纲生成
  - 提供关键点和资源建议

- **`save_blog_post`** - 保存博文到指定路径
- **`analyze_blog_performance`** - 分析博文性能指标

### 客栈管理服务器功能

- **`design_guesthouse_space`** - 设计客栈空间
  - 整合纳西族文化元素
  - 提供设计建议和布局方案

- **`create_marketing_content`** - 创建营销内容
  - 支持小红书、抖音、微信等平台
  - 针对不同平台优化内容风格

- **`plan_cultural_activities`** - 规划文化活动
  - 传统手工艺体验
  - 文化节庆活动安排

- **`generate_authenticity_guidelines`** - 生成文化真实性指南
- **`create_implementation_checklist`** - 创建实施清单

### 媒体生成服务器功能

- **`generate_blog_images`** - 为博客生成相关图片
- **`create_featured_image`** - 创建博客特色图片
- **`generate_social_media_images`** - 生成社交媒体图片
- **`edit_existing_image`** - 编辑现有图片
- **`optimize_image_for_web`** - 优化图片以适合网页
- **`prepare_for_future_video_generation`** - 为未来视频生成做准备

### 博客管理服务器功能

- **`publish_blog_post`** - 发布博文
- **`build_site`** - 构建 Zola 网站
- **`backup_blog`** - 备份博客
- **`analyze_site_performance`** - 分析网站性能
- **`manage_content_files`** - 管理内容文件
- **`deploy_to_production`** - 部署到生产环境

## 📝 使用示例

### 创建博文

```python
# 通过 MCP 调用
request = {
    "topic": "AI 在丽江客栈设计中的应用",
    "category": "技术",
    "tags": ["AI", "建筑设计", "客栈"],
    "style": "professional",
    "target_length": "medium",
    "include_code": true,
    "include_images": true
}

result = await create_blog_post(request)
```

### 生成客栈设计方案

```python
request = {
    "space_type": "reception_area",
    "size": "20平方米",
    "cultural_elements": ["纳西族", "传统"],
    "style": "modern_traditional",
    "budget": "medium"
}

design = await design_guesthouse_space(request)
```

### 生成营销图片

```python
result = await create_featured_image(
    blog_title="丽江客栈的现代化改造",
    blog_summary="探索传统与现代的完美结合",
    style="modern"
)
```

## 🔧 配置说明

### 环境变量

```bash
# OpenAI API (用于 DALL-E)
OPENAI_API_KEY=your_openai_key

# Azure OpenAI (可选)
AZURE_OPENAI_API_KEY=your_azure_key
AZURE_OPENAI_ENDPOINT=your_azure_endpoint
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# DeepSeek API
DEEPSEEK_API_KEY=your_deepseek_key
DEEPSEEK_BASE_URL=https://api.deepseek.com

# 博客路径
BLOG_CONTENT_PATH=/path/to/your/blog/content
BLOG_STATIC_PATH=/path/to/your/blog/static

# 日志级别
LOG_LEVEL=INFO
```

### 博客结构

系统假设以下 Zola 博客结构：

```
blog/
├── content/
│   ├── blog/           # 博文目录
│   ├── about/          # 关于页面
│   └── _index.md
├── static/
│   ├── images/         # 图片资源
│   └── css/
├── templates/
└── config.toml
```

## 🐛 故障排除

### 常见问题

1. **导入错误**
   - 确保使用 `poetry run` 运行 Python 命令
   - 检查 PYTHONPATH 设置

2. **API 密钥错误**
   - 验证 `.env` 文件中的 API 密钥
   - 检查 Azure OpenAI 端点格式

3. **文件路径错误**
   - 确保博客路径配置正确
   - 检查目录权限

### 调试模式

设置环境变量启用详细日志：

```bash
export LOG_LEVEL=DEBUG
poetry run python -m blog_mcp_server.content_server
```

## 🔄 更新和维护

### 添加新功能

1. 在相应的服务器文件中添加新的 `@mcp.tool()` 函数
2. 更新相关的服务类（如 `ContentService`、`AIService`）
3. 添加相应的测试
4. 更新文档

### 升级依赖

```bash
poetry update
poetry run pytest  # 运行测试确保兼容性
```

## 📚 API 参考

详细的 API 文档可以通过运行服务器并连接 MCP 客户端查看。每个工具都包含详细的参数说明和返回值格式。

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request

## 📄 许可证

此项目为私有项目，仅供 Polly 的博客和客栈项目使用。

---

**注意**: 这是一个基于 FastMCP 的高级 AI 驱动系统，需要相应的 API 密钥和配置才能完全运行。确保在生产环境中妥善保护你的 API 密钥。
