"""
媒体生成 MCP 服务器
提供图片生成、图片处理、未来支持视频生成等功能
"""
import asyncio
import logging
import base64
import io
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import httpx
from PIL import Image

from fastmcp import FastMCP
from pydantic import BaseModel

from .config import Config
from .services.ai_service import AIService
from .utils.zola_utils import ZolaUtils

# 配置日志
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

# 创建 MCP 应用
mcp = FastMCP("Media Generation Server")

# 初始化服务
ai_service = AIService()
zola_utils = ZolaUtils()

class ImageGenerationRequest(BaseModel):
    """图片生成请求模型"""
    prompt: str
    style: str = "realistic"  # realistic, illustration, artistic, technical
    size: str = "1792x1024"
    quality: str = "standard"  # standard, hd
    count: int = 1
    blog_context: Optional[str] = None  # 博文上下文，用于优化提示词

class ImageOptimizationRequest(BaseModel):
    """图片优化请求模型"""
    image_path: str
    optimization_type: str = "web"  # web, print, social
    target_size: Optional[str] = None
    quality: int = 85
    format: str = "JPEG"  # JPEG, PNG, WebP

class BlogImageRequest(BaseModel):
    """博文图片生成请求模型"""
    blog_title: str
    blog_content: str
    image_type: str = "cover"  # cover, illustration, diagram, screenshot
    section_context: Optional[str] = None
    target_mood: str = "professional"  # professional, casual, inspiring, technical

@mcp.tool()
async def generate_image(request: ImageGenerationRequest) -> Dict[str, Any]:
    """
    生成图片
    
    Args:
        request: 图片生成请求
        
    Returns:
        生成的图片信息
    """
    try:
        logger.info(f"开始生成图片: {request.prompt[:50]}...")
        
        # 优化提示词
        optimized_prompt = await _optimize_image_prompt(
            request.prompt, 
            request.style, 
            request.blog_context
        )
        
        # 生成图片
        image_result = await ai_service.generate_image(
            prompt=optimized_prompt,
            size=request.size,
            quality=request.quality
        )
        
        # 下载和保存图片
        saved_path = await _download_and_save_image(
            image_result["url"], 
            request.prompt,
            request.style
        )
        
        result = {
            "original_prompt": request.prompt,
            "optimized_prompt": optimized_prompt,
            "revised_prompt": image_result.get("revised_prompt"),
            "image_url": image_result["url"],
            "local_path": saved_path,
            "size": request.size,
            "quality": request.quality,
            "style": request.style,
            "generated_at": datetime.now().isoformat()
        }
        
        logger.info(f"图片生成完成: {saved_path}")
        return result
        
    except Exception as e:
        logger.error(f"生成图片时出错: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def generate_blog_image(request: BlogImageRequest) -> Dict[str, Any]:
    """
    为博文生成专门的图片
    
    Args:
        request: 博文图片生成请求
        
    Returns:
        生成的博文图片信息
    """
    try:
        logger.info(f"开始为博文生成图片: {request.blog_title}")
        
        # 根据博文内容和类型生成提示词
        prompt = await _generate_blog_image_prompt(request)
        
        # 生成图片
        image_request = ImageGenerationRequest(
            prompt=prompt,
            style=_get_style_for_image_type(request.image_type),
            blog_context=f"{request.blog_title}: {request.blog_content[:500]}"
        )
        
        image_result = await generate_image(image_request)
        
        # 添加博文相关信息
        if "error" not in image_result:
            image_result.update({
                "blog_title": request.blog_title,
                "image_type": request.image_type,
                "target_mood": request.target_mood,
                "usage_suggestion": _get_usage_suggestion(request.image_type),
                "alt_text": _generate_alt_text(request.blog_title, request.image_type)
            })
        
        logger.info(f"博文图片生成完成: {request.image_type}")
        return image_result
        
    except Exception as e:
        logger.error(f"生成博文图片时出错: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def optimize_image(request: ImageOptimizationRequest) -> Dict[str, Any]:
    """
    优化图片
    
    Args:
        request: 图片优化请求
        
    Returns:
        优化后的图片信息
    """
    try:
        logger.info(f"开始优化图片: {request.image_path}")
        
        input_path = Path(request.image_path)
        if not input_path.exists():
            return {"error": "图片文件不存在"}
        
        # 打开图片
        with Image.open(input_path) as img:
            # 获取原始信息
            original_size = img.size
            original_format = img.format
            original_mode = img.mode
            
            # 转换颜色模式（如果需要）
            if request.format.upper() == "JPEG" and img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")
            
            # 调整大小（如果指定）
            if request.target_size:
                try:
                    width, height = map(int, request.target_size.split('x'))
                    img = img.resize((width, height), Image.Resampling.LANCZOS)
                except ValueError:
                    logger.warning(f"无效的目标尺寸: {request.target_size}")
            
            # 生成输出文件名
            output_path = input_path.parent / f"{input_path.stem}_optimized{_get_file_extension(request.format)}"
            
            # 保存优化后的图片
            save_kwargs = {"quality": request.quality}
            if request.format.upper() == "PNG":
                save_kwargs = {"optimize": True}
            elif request.format.upper() == "WEBP":
                save_kwargs = {"quality": request.quality, "method": 6}
            
            img.save(output_path, format=request.format.upper(), **save_kwargs)
        
        # 获取文件大小信息
        original_size_bytes = input_path.stat().st_size
        optimized_size_bytes = output_path.stat().st_size
        compression_ratio = (1 - optimized_size_bytes / original_size_bytes) * 100
        
        result = {
            "original_path": str(input_path),
            "optimized_path": str(output_path),
            "original_format": original_format,
            "optimized_format": request.format.upper(),
            "original_size": original_size,
            "optimized_size": Image.open(output_path).size,
            "original_file_size": original_size_bytes,
            "optimized_file_size": optimized_size_bytes,
            "compression_ratio": round(compression_ratio, 2),
            "optimization_type": request.optimization_type,
            "optimized_at": datetime.now().isoformat()
        }
        
        logger.info(f"图片优化完成，压缩比: {compression_ratio:.1f}%")
        return result
        
    except Exception as e:
        logger.error(f"优化图片时出错: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def batch_generate_images(prompts: List[str], style: str = "realistic") -> Dict[str, Any]:
    """
    批量生成图片
    
    Args:
        prompts: 提示词列表
        style: 图片风格
        
    Returns:
        批量生成结果
    """
    try:
        logger.info(f"开始批量生成图片，数量: {len(prompts)}")
        
        results = []
        failed_count = 0
        
        for i, prompt in enumerate(prompts):
            try:
                request = ImageGenerationRequest(prompt=prompt, style=style)
                result = await generate_image(request)
                
                if "error" in result:
                    failed_count += 1
                    logger.warning(f"第{i+1}张图片生成失败: {result['error']}")
                else:
                    logger.info(f"第{i+1}张图片生成成功")
                
                results.append({
                    "index": i + 1,
                    "prompt": prompt,
                    "result": result
                })
                
                # 添加延迟以避免API限制
                if i < len(prompts) - 1:
                    await asyncio.sleep(Config.API_DELAY)
                    
            except Exception as e:
                failed_count += 1
                logger.error(f"生成第{i+1}张图片时出错: {str(e)}")
                results.append({
                    "index": i + 1,
                    "prompt": prompt,
                    "result": {"error": str(e)}
                })
        
        summary = {
            "total_count": len(prompts),
            "success_count": len(prompts) - failed_count,
            "failed_count": failed_count,
            "success_rate": round((len(prompts) - failed_count) / len(prompts) * 100, 1),
            "results": results,
            "generated_at": datetime.now().isoformat()
        }
        
        logger.info(f"批量生成完成，成功率: {summary['success_rate']}%")
        return summary
        
    except Exception as e:
        logger.error(f"批量生成图片时出错: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def analyze_image_content(image_path: str, analysis_type: str = "general") -> Dict[str, Any]:
    """
    分析图片内容
    
    Args:
        image_path: 图片路径
        analysis_type: 分析类型 (general, technical, artistic, accessibility)
        
    Returns:
        图片分析结果
    """
    try:
        logger.info(f"开始分析图片内容: {image_path}")
        
        path = Path(image_path)
        if not path.exists():
            return {"error": "图片文件不存在"}
        
        # 上传图片到临时服务（简化处理，实际可能需要上传到云服务）
        # 这里假设图片可以通过URL访问
        image_url = f"file://{path.absolute()}"
        
        # 构建分析查询
        queries = {
            "general": "请描述这张图片的内容、风格和主要元素",
            "technical": "请分析这张图片的技术特征，包括构图、色彩、光线等",
            "artistic": "请从艺术角度分析这张图片的美学价值和表现手法",
            "accessibility": "请为视觉障碍用户生成这张图片的详细替代文本"
        }
        
        query = queries.get(analysis_type, queries["general"])
        
        # 分析图片（注意：这需要支持视觉的AI模型）
        try:
            analysis_result = await ai_service.analyze_image(image_url, query)
        except Exception:
            # 如果不支持图片分析，返回基本信息
            with Image.open(path) as img:
                analysis_result = f"图片尺寸: {img.size}, 格式: {img.format}, 颜色模式: {img.mode}"
        
        # 获取图片基本信息
        with Image.open(path) as img:
            basic_info = {
                "file_path": str(path),
                "file_size": path.stat().st_size,
                "dimensions": img.size,
                "format": img.format,
                "mode": img.mode,
                "has_transparency": img.mode in ("RGBA", "LA") or "transparency" in img.info
            }
        
        result = {
            "basic_info": basic_info,
            "analysis_type": analysis_type,
            "analysis_result": analysis_result,
            "suggestions": _get_image_suggestions(analysis_type, basic_info),
            "analyzed_at": datetime.now().isoformat()
        }
        
        logger.info(f"图片分析完成: {analysis_type}")
        return result
        
    except Exception as e:
        logger.error(f"分析图片内容时出错: {str(e)}")
        return {"error": str(e)}

async def _optimize_image_prompt(prompt: str, style: str, blog_context: Optional[str]) -> str:
    """优化图片生成提示词"""
    
    style_keywords = {
        "realistic": "photorealistic, high quality, detailed",
        "illustration": "digital illustration, artistic, stylized",
        "artistic": "artistic, creative, expressive",
        "technical": "technical diagram, clean, professional"
    }
    
    base_enhancement = style_keywords.get(style, "high quality")
    
    if blog_context:
        # 使用AI优化提示词
        optimization_prompt = f"""
请优化以下图片生成提示词，使其更适合技术博客使用：

原始提示词: {prompt}
图片风格: {style}
博文上下文: {blog_context[:200]}...

请返回优化后的英文提示词，要求：
1. 清晰描述图片内容
2. 符合{style}风格
3. 适合技术博客使用
4. 包含适当的技术关键词

优化后的提示词:
"""
        try:
            optimized = await ai_service.generate_text(optimization_prompt, temperature=0.5)
            return f"{optimized}, {base_enhancement}"
        except:
            pass
    
    return f"{prompt}, {base_enhancement}"

async def _download_and_save_image(image_url: str, prompt: str, style: str) -> str:
    """下载并保存图片"""
    
    # 创建输出目录
    output_dir = Path(Config.OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_prompt = safe_prompt.replace(' ', '_')
    filename = f"{timestamp}_{safe_prompt}_{style}.png"
    file_path = output_dir / filename
    
    # 下载图片
    async with httpx.AsyncClient() as client:
        response = await client.get(image_url)
        response.raise_for_status()
        
        with open(file_path, 'wb') as f:
            f.write(response.content)
    
    return str(file_path)

async def _generate_blog_image_prompt(request: BlogImageRequest) -> str:
    """生成博文图片的提示词"""
    
    image_type_prompts = {
        "cover": f"Blog cover image for '{request.blog_title}', professional and engaging",
        "illustration": f"Technical illustration for blog post about {request.blog_title}",
        "diagram": f"Technical diagram or flowchart related to {request.blog_title}",
        "screenshot": f"Clean interface screenshot or mockup for {request.blog_title}"
    }
    
    base_prompt = image_type_prompts.get(request.image_type, f"Image for {request.blog_title}")
    
    # 分析博文内容提取关键词
    content_keywords = await _extract_keywords_from_content(request.blog_content)
    
    if content_keywords:
        base_prompt += f", featuring {', '.join(content_keywords[:3])}"
    
    if request.section_context:
        base_prompt += f", specifically about {request.section_context}"
    
    mood_keywords = {
        "professional": "professional, clean, modern",
        "casual": "friendly, approachable, warm",
        "inspiring": "inspiring, motivational, uplifting",
        "technical": "technical, precise, detailed"
    }
    
    base_prompt += f", {mood_keywords.get(request.target_mood, 'professional')}"
    
    return base_prompt

async def _extract_keywords_from_content(content: str) -> List[str]:
    """从博文内容中提取关键词"""
    
    # 简单的关键词提取（实际项目中可以使用更复杂的NLP技术）
    tech_keywords = [
        "AI", "机器学习", "深度学习", "神经网络", "算法", "数据", "编程", "代码",
        "Python", "JavaScript", "React", "Vue", "Node.js", "API", "数据库",
        "云计算", "DevOps", "Docker", "Kubernetes", "微服务", "架构"
    ]
    
    found_keywords = []
    content_lower = content.lower()
    
    for keyword in tech_keywords:
        if keyword.lower() in content_lower or keyword in content:
            found_keywords.append(keyword)
    
    return found_keywords[:5]  # 返回前5个关键词

def _get_style_for_image_type(image_type: str) -> str:
    """根据图片类型获取推荐风格"""
    
    style_map = {
        "cover": "artistic",
        "illustration": "illustration", 
        "diagram": "technical",
        "screenshot": "realistic"
    }
    
    return style_map.get(image_type, "realistic")

def _get_usage_suggestion(image_type: str) -> str:
    """获取图片使用建议"""
    
    suggestions = {
        "cover": "建议用作文章封面图片，在文章开头显示",
        "illustration": "建议插入到相关段落中，配合文字说明",
        "diagram": "建议用于解释复杂概念，添加详细说明",
        "screenshot": "建议展示具体操作步骤，配合代码示例"
    }
    
    return suggestions.get(image_type, "根据内容需要合理使用")

def _generate_alt_text(blog_title: str, image_type: str) -> str:
    """生成图片的alt文本"""
    
    return f"{image_type.title()} image for blog post: {blog_title}"

def _get_file_extension(format_name: str) -> str:
    """获取文件扩展名"""
    
    extensions = {
        "JPEG": ".jpg",
        "PNG": ".png", 
        "WEBP": ".webp",
        "GIF": ".gif"
    }
    
    return extensions.get(format_name.upper(), ".jpg")

def _get_image_suggestions(analysis_type: str, basic_info: Dict[str, Any]) -> List[str]:
    """获取图片改进建议"""
    
    suggestions = []
    
    # 基于文件大小的建议
    file_size_mb = basic_info["file_size"] / (1024 * 1024)
    if file_size_mb > 2:
        suggestions.append("考虑压缩图片以减小文件大小")
    
    # 基于尺寸的建议
    width, height = basic_info["dimensions"]
    if width > 2000 or height > 2000:
        suggestions.append("对于网页使用，可以考虑缩小图片尺寸")
    
    # 基于格式的建议
    if basic_info["format"] == "PNG" and not basic_info["has_transparency"]:
        suggestions.append("如不需要透明度，建议转换为JPEG格式以减小文件大小")
    
    return suggestions

def main():
    """主函数，启动 MCP 服务器"""
    try:
        # 验证配置
        Config.validate()
        logger.info("媒体生成服务器启动中...")
        mcp.run()
    except Exception as e:
        logger.error(f"启动服务器时出错: {str(e)}")
        raise

if __name__ == "__main__":
    main()
