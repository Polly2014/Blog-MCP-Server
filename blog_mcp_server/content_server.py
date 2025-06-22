"""
博文内容创作 MCP 服务器
提供博文写作、内容优化、格式化等功能
"""
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from pydantic import BaseModel

from .config import Config
from .services.content_service import ContentService
from .services.ai_service import AIService
from .utils.zola_utils import ZolaUtils

# 配置日志
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

# 创建 FastMCP 应用
mcp = FastMCP("Blog Content Server")

# 初始化服务
content_service = ContentService()
ai_service = AIService()
zola_utils = ZolaUtils()

class BlogPostRequest(BaseModel):
    """博文创建请求模型"""
    topic: str
    content_outline: Optional[str] = None
    category: str = "技术"
    tags: List[str] = []
    style: str = "professional"  # professional, casual, academic
    target_length: str = "medium"  # short, medium, long
    include_code: bool = True
    include_images: bool = True

class BlogOptimizationRequest(BaseModel):
    """博文优化请求模型"""
    content: str
    optimization_type: str = "seo"  # seo, readability, engagement
    target_keywords: List[str] = []

@mcp.tool()
async def create_blog_post(request: BlogPostRequest) -> Dict[str, Any]:
    """
    创建完整的博文，包括内容生成和 frontmatter
    
    Args:
        request: 博文创建请求，包含主题、分类、标签等信息
        
    Returns:
        包含生成的博文内容、frontmatter 和文件路径的字典
    """
    try:
        logger.info(f"开始创建博文: {request.topic}")
        
        # 1. 生成博文内容
        blog_content = await content_service.generate_blog_content(
            topic=request.topic,
            outline=request.content_outline,
            style=request.style,
            target_length=request.target_length,
            include_code=request.include_code
        )
        
        # 2. 生成 frontmatter
        frontmatter = zola_utils.generate_frontmatter(
            title=blog_content["title"],
            category=request.category,
            tags=request.tags,
            summary=blog_content["summary"]
        )
        
        # 3. 组合完整的博文
        full_content = f"{frontmatter}\n\n{blog_content['content']}"
        
        # 4. 生成文件路径
        slug = zola_utils.generate_slug(blog_content["title"])
        file_path = Config.BLOG_CONTENT_PATH / "blog" / f"{slug}.md"
        
        # 5. 建议图片位置（如果需要）
        image_suggestions = []
        if request.include_images:
            image_suggestions = content_service.suggest_image_positions(blog_content["content"])
        
        result = {
            "title": blog_content["title"],
            "content": full_content,
            "file_path": str(file_path),
            "slug": slug,
            "frontmatter": frontmatter,
            "summary": blog_content["summary"],
            "image_suggestions": image_suggestions,
            "estimated_reading_time": content_service.estimate_reading_time(blog_content["content"])
        }
        
        logger.info(f"博文创建完成: {blog_content['title']}")
        return result
        
    except Exception as e:
        logger.error(f"创建博文时出错: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def optimize_blog_content(request: BlogOptimizationRequest) -> Dict[str, Any]:
    """
    优化博文内容，改善 SEO、可读性或参与度
    
    Args:
        request: 优化请求，包含原始内容和优化类型
        
    Returns:
        优化后的内容和改进建议
    """
    try:
        logger.info(f"开始优化博文内容，类型: {request.optimization_type}")
        
        optimized_content = await content_service.optimize_content(
            content=request.content,
            optimization_type=request.optimization_type,
            keywords=request.target_keywords
        )
        
        return {
            "original_content": request.content,
            "optimized_content": optimized_content["content"],
            "improvements": optimized_content["improvements"],
            "seo_score": optimized_content.get("seo_score"),
            "readability_score": optimized_content.get("readability_score")
        }
        
    except Exception as e:
        logger.error(f"优化博文内容时出错: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def generate_blog_outline(topic: str, depth: str = "medium") -> Dict[str, Any]:
    """
    根据主题生成博文大纲
    
    Args:
        topic: 博文主题
        depth: 大纲深度 (shallow, medium, deep)
        
    Returns:
        生成的大纲结构
    """
    try:
        logger.info(f"生成博文大纲: {topic}")
        
        outline = await content_service.generate_outline(topic, depth)
        
        return {
            "topic": topic,
            "outline": outline["structure"],
            "estimated_length": outline["estimated_length"],
            "key_points": outline["key_points"],
            "suggested_resources": outline.get("resources", [])
        }
        
    except Exception as e:
        logger.error(f"生成大纲时出错: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def save_blog_post(file_path: str, content: str) -> Dict[str, Any]:
    """
    保存博文到指定路径
    
    Args:
        file_path: 文件保存路径
        content: 博文内容
        
    Returns:
        保存结果信息
    """
    try:
        path = Path(file_path)
        
        # 确保目录存在
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入文件
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"博文已保存到: {file_path}")
        
        return {
            "success": True,
            "file_path": file_path,
            "file_size": path.stat().st_size,
            "saved_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"保存博文时出错: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def analyze_blog_performance(file_path: str) -> Dict[str, Any]:
    """
    分析博文的性能指标
    
    Args:
        file_path: 博文文件路径
        
    Returns:
        性能分析结果
    """
    try:
        logger.info(f"分析博文性能: {file_path}")
        
        path = Path(file_path)
        if not path.exists():
            return {"error": "文件不存在"}
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        analysis = await content_service.analyze_content_performance(content)
        
        return {
            "file_path": file_path,
            "word_count": analysis["word_count"],
            "reading_time": analysis["reading_time"],
            "seo_score": analysis["seo_score"],
            "readability_score": analysis["readability_score"],
            "engagement_potential": analysis["engagement_potential"],
            "improvement_suggestions": analysis["suggestions"]
        }
        
    except Exception as e:
        logger.error(f"分析博文性能时出错: {str(e)}")
        return {"error": str(e)}

def main():
    """主函数，启动 MCP 服务器"""
    try:
        # 验证配置
        Config.validate()
        logger.info("博文内容服务器启动中...")
        mcp.run()
    except Exception as e:
        logger.error(f"启动服务器时出错: {str(e)}")
        raise

if __name__ == "__main__":
    main()
