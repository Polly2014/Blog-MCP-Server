# Blog MCP Server

这是为 Polly 博客系统设计的 MCP 服务器集群，支持博文创作、客栈运营管理和媒体生成等功能。

## 功能模块

### 1. Blog Content Server
- 博文内容生成和优化
- 技术文档写作辅助
- 内容结构化和格式化
- Frontmatter 自动生成

### 2. Guesthouse Management Server  
- 丽江客栈设计方案生成
- 营销文案创作
- 文化元素整合建议
- 客户体验优化方案

### 3. Media Generation Server
- DALL-E 图片生成
- 图片优化和处理
- 未来支持 Sora 视频生成
- 媒体资源管理

### 4. Blog Management Server
- Zola 博客系统管理
- 文件操作和部署
- 内容发布和更新
- 备份和版本控制

## 安装和配置

### 1. 安装依赖
```bash
cd Blog_MCP_Server
poetry install
```

### 2. 配置环境变量
复制 `.env.example` 到 `.env` 并填入相应的 API 密钥：
```bash
cp .env.example .env
```

### 3. 启动服务器
```bash
# 启动博文内容服务器
poetry run blog-content-server

# 启动客栈管理服务器  
poetry run guesthouse-server

# 启动媒体生成服务器
poetry run media-generation-server

# 启动博客管理服务器
poetry run blog-management-server
```

## VS Code 配置

在 VS Code 的 `settings.json` 中添加以下配置：

```json
"mcp": {
  "servers": {
    "blog-content": {
      "command": "/Users/polly/.local/bin/poetry",
      "args": ["-C", "/path/to/Blog_MCP_Server", "run", "blog-content-server"],
      "env": {}
    },
    "guesthouse": {
      "command": "/Users/polly/.local/bin/poetry", 
      "args": ["-C", "/path/to/Blog_MCP_Server", "run", "guesthouse-server"],
      "env": {}
    },
    "media-generation": {
      "command": "/Users/polly/.local/bin/poetry",
      "args": ["-C", "/path/to/Blog_MCP_Server", "run", "media-generation-server"], 
      "env": {}
    },
    "blog-management": {
      "command": "/Users/polly/.local/bin/poetry",
      "args": ["-C", "/path/to/Blog_MCP_Server", "run", "blog-management-server"],
      "env": {}
    }
  }
}
```

## 项目结构

```
Blog_MCP_Server/
├── pyproject.toml
├── README.md
├── .env.example
├── blog_mcp_server/
│   ├── __init__.py
│   ├── config.py
│   ├── content_server.py      # 博文内容创作服务器
│   ├── guesthouse_server.py   # 客栈运营服务器
│   ├── media_server.py        # 媒体生成服务器
│   ├── management_server.py   # 博客管理服务器
│   ├── models/
│   │   ├── __init__.py
│   │   ├── blog.py           # 博文数据模型
│   │   ├── guesthouse.py     # 客栈数据模型
│   │   └── media.py          # 媒体数据模型
│   ├── services/
│   │   ├── __init__.py
│   │   ├── content_service.py    # 内容服务
│   │   ├── ai_service.py         # AI 服务集成
│   │   ├── media_service.py      # 媒体处理服务
│   │   └── file_service.py       # 文件操作服务
│   ├── templates/
│   │   ├── blog_post.md.j2       # 博文模板
│   │   ├── frontmatter.toml.j2   # Frontmatter 模板
│   │   └── guesthouse_plan.md.j2 # 客栈方案模板
│   └── utils/
│       ├── __init__.py
│       ├── zola_utils.py         # Zola 相关工具
│       ├── prompt_utils.py       # 提示词工具
│       └── image_utils.py        # 图片处理工具
├── tests/
│   ├── __init__.py
│   ├── test_content_server.py
│   ├── test_guesthouse_server.py
│   ├── test_media_server.py
│   └── test_management_server.py
└── docs/
    ├── api.md
    ├── usage.md
    └── examples.md
```

## 开发指南

### 添加新功能
1. 在相应的服务器文件中添加新的工具函数
2. 更新数据模型（如需要）
3. 添加单元测试
4. 更新文档

### 调试
使用 Python 调试器或添加日志来调试 MCP 服务器：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 贡献

欢迎提交 Pull Request 和 Issue！
