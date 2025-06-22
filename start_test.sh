#!/bin/bash

# Blog MCP Server 测试启动脚本
# 用于测试所有 MCP 服务器是否正常工作

echo "🚀 启动 Blog MCP Server 系统测试..."
echo "=================================="

# 进入项目目录
cd "$(dirname "$0")"

# 检查 Poetry 环境
echo "📦 检查 Poetry 环境..."
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry 未安装，请先安装 Poetry"
    exit 1
fi

# 安装依赖
echo "📚 安装依赖..."
poetry install

# 检查环境变量
echo "🔧 检查环境变量..."
if [ ! -f ".env" ]; then
    echo "❌ .env 文件不存在，请复制 .env.example 并配置"
    exit 1
fi

# 测试各个服务器
echo ""
echo "🧪 测试各个 MCP 服务器..."
echo "=================================="

# 测试博客内容服务器
echo "1. 测试博客内容服务器..."
poetry run python -c "
try:
    from blog_mcp_server.content_server import mcp
    print('✅ 博客内容服务器导入成功')
except Exception as e:
    print(f'❌ 博客内容服务器导入失败: {e}')
"

# 测试客栈管理服务器
echo "2. 测试客栈管理服务器..."
poetry run python -c "
try:
    from blog_mcp_server.guesthouse_server import mcp
    print('✅ 客栈管理服务器导入成功')
except Exception as e:
    print(f'❌ 客栈管理服务器导入失败: {e}')
"

# 测试媒体生成服务器
echo "3. 测试媒体生成服务器..."
poetry run python -c "
try:
    from blog_mcp_server.media_server import mcp
    print('✅ 媒体生成服务器导入成功')
except Exception as e:
    print(f'❌ 媒体生成服务器导入失败: {e}')
"

# 测试博客管理服务器
echo "4. 测试博客管理服务器..."
poetry run python -c "
try:
    from blog_mcp_server.management_server import mcp
    print('✅ 博客管理服务器导入成功')
except Exception as e:
    print(f'❌ 博客管理服务器导入失败: {e}')
"

echo ""
echo "🔍 检查配置..."
echo "=================================="

# 检查配置
poetry run python -c "
try:
    from blog_mcp_server.config import Config
    Config.validate()
    print('✅ 配置验证成功')
    print(f'📁 博客路径: {Config.BLOG_CONTENT_PATH}')
    print(f'📁 静态资源路径: {Config.BLOG_STATIC_PATH}')
except Exception as e:
    print(f'❌ 配置验证失败: {e}')
"

echo ""
echo "📋 使用说明..."
echo "=================================="
echo "1. 复制 mcp-settings.json 中的配置到你的 VS Code settings.json"
echo "2. 在 VS Code 中重启 MCP 连接"
echo "3. 使用 Claude 或其他 MCP 客户端连接服务器"
echo ""
echo "🛠️ 可用的 MCP 服务器："
echo "  - blog-content-server: 博客内容创作"
echo "  - guesthouse-management-server: 客栈管理"
echo "  - media-generation-server: 媒体生成"
echo "  - blog-management-server: 博客系统管理"
echo ""
echo "✨ 测试完成！"
