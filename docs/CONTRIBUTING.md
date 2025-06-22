# Contributing to Blog MCP Server

欢迎贡献代码！以下是参与项目的指南。

## 开发环境设置

1. **克隆仓库**
```bash
git clone git@github.com:Polly2014/Blog-MCP-Server.git
cd Blog-MCP-Server
```

2. **安装依赖**
```bash
poetry install
```

3. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，添加你的 API keys
```

4. **运行测试**
```bash
poetry run pytest tests/
```

## 代码规范

### Python 代码风格
- 遵循 PEP 8 标准
- 使用 type hints
- 函数和类都需要 docstrings
- 最大行长度 88 字符

### 提交信息格式
使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

例如：
- `feat: add new blog generation template`
- `fix: resolve AI service timeout issue`
- `docs: update API reference`

### 分支策略
- `main`: 主分支，保持稳定
- `develop`: 开发分支
- `feature/xxx`: 功能分支
- `fix/xxx`: 修复分支

## 新功能开发

1. **创建功能分支**
```bash
git checkout -b feature/new-feature
```

2. **开发和测试**
- 编写代码
- 添加测试
- 更新文档

3. **提交更改**
```bash
git add .
git commit -m "feat: add new feature description"
```

4. **创建 Pull Request**
- 推送分支到远程仓库
- 在 GitHub 上创建 Pull Request
- 等待代码审查

## 测试指南

### 单元测试
```bash
poetry run pytest tests/test_servers.py -v
```

### 集成测试
```bash
poetry run pytest tests/test_ai_service.py -v
```

### 手动测试
```bash
./start_test.sh
```

## AI Provider 支持

### 添加新的 AI Provider

1. **在 `ai_service.py` 中添加客户端初始化**
2. **实现 `_generate_with_[provider]` 方法**
3. **更新 `get_available_providers` 方法**
4. **添加相应的环境变量配置**

### 示例：添加 Claude 支持

```python
# 在 AIService.__init__ 中
if os.getenv('ANTHROPIC_API_KEY'):
    import anthropic
    self.anthropic_client = anthropic.Anthropic(
        api_key=os.getenv('ANTHROPIC_API_KEY')
    )

# 添加生成方法
async def _generate_with_claude(self, prompt: str, **kwargs) -> str:
    response = await self.anthropic_client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=kwargs.get('max_tokens', 2000),
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text
```

## 文档更新

- API 更改需要更新 `docs/API_REFERENCE.md`
- 新功能需要更新 `README.md` 和 `USAGE_GUIDE.md`
- 配置更改需要更新 `.env.example`

## 性能优化

### 缓存策略
- 使用内存缓存存储频繁访问的数据
- 考虑 Redis 用于分布式缓存

### 并发处理
- 使用 `asyncio` 进行异步处理
- 合理设置 AI API 调用的并发限制

## 问题报告

请使用 GitHub Issues 报告问题，包含：
- 详细的问题描述
- 重现步骤
- 系统环境信息
- 相关的日志信息

## 许可证

本项目使用 MIT 许可证。贡献代码即表示同意将代码以相同许可证开源。
