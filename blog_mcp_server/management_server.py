"""
博客管理 MCP 服务器
提供博客系统管理、文件操作、发布部署等功能
"""
import asyncio
import logging
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from pydantic import BaseModel

from .config import Config
from .services.ai_service import AIService
from .utils.zola_utils import ZolaUtils

# 配置日志
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

# 创建 MCP 应用
mcp = FastMCP("Blog Management Server")

# 初始化服务
ai_service = AIService()
zola_utils = ZolaUtils()

class PublishRequest(BaseModel):
    """发布请求模型"""
    file_path: str
    auto_build: bool = True
    auto_deploy: bool = False
    commit_message: Optional[str] = None

class BackupRequest(BaseModel):
    """备份请求模型"""
    backup_type: str = "full"  # full, content_only, config_only
    include_generated: bool = False
    compression: bool = True

class SiteAnalysisRequest(BaseModel):
    """网站分析请求模型"""
    analysis_type: str = "overview"  # overview, performance, seo, content
    date_range: int = 30  # 天数

@mcp.tool()
async def publish_blog_post(request: PublishRequest) -> Dict[str, Any]:
    """
    发布博文
    
    Args:
        request: 发布请求
        
    Returns:
        发布结果
    """
    try:
        logger.info(f"开始发布博文: {request.file_path}")
        
        file_path = Path(request.file_path)
        if not file_path.exists():
            return {"error": "文件不存在"}
        
        # 验证文件内容
        validation_result = zola_utils.validate_content(file_path.read_text(encoding='utf-8'))
        if not validation_result["valid"]:
            return {
                "error": "文件验证失败",
                "issues": validation_result["issues"],
                "warnings": validation_result["warnings"]
            }
        
        results = {
            "file_path": str(file_path),
            "validation": validation_result,
            "published_at": datetime.now().isoformat()
        }
        
        # 构建网站
        if request.auto_build:
            build_result = zola_utils.build_site()
            results["build_result"] = build_result
            
            if not build_result["success"]:
                return {
                    "error": "构建失败",
                    "build_output": build_result
                }
        
        # 自动部署（如果启用）
        if request.auto_deploy:
            deploy_result = await _deploy_site(request.commit_message or f"发布: {file_path.name}")
            results["deploy_result"] = deploy_result
        
        logger.info(f"博文发布成功: {file_path.name}")
        return results
        
    except Exception as e:
        logger.error(f"发布博文时出错: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def build_site() -> Dict[str, Any]:
    """
    构建网站
    
    Returns:
        构建结果
    """
    try:
        logger.info("开始构建网站")
        
        result = zola_utils.build_site()
        
        if result["success"]:
            # 获取构建统计信息
            public_dir = Config.BLOG_ROOT_PATH / "public"
            if public_dir.exists():
                stats = _get_build_stats(public_dir)
                result.update(stats)
        
        logger.info(f"网站构建完成，成功: {result['success']}")
        return result
        
    except Exception as e:
        logger.error(f"构建网站时出错: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def serve_development_site(port: int = 1111) -> Dict[str, Any]:
    """
    启动开发服务器
    
    Args:
        port: 服务器端口
        
    Returns:
        启动结果
    """
    try:
        logger.info(f"启动开发服务器，端口: {port}")
        
        result = zola_utils.serve_site(port)
        
        logger.info(f"开发服务器启动: {result['success']}")
        return result
        
    except Exception as e:
        logger.error(f"启动开发服务器时出错: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def backup_blog(request: BackupRequest) -> Dict[str, Any]:
    """
    备份博客
    
    Args:
        request: 备份请求
        
    Returns:
        备份结果
    """
    try:
        logger.info(f"开始备份博客: {request.backup_type}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"blog_backup_{request.backup_type}_{timestamp}"
        backup_dir = Config.BLOG_ROOT_PATH.parent / "backups" / backup_name
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 根据备份类型选择文件
        if request.backup_type == "full":
            # 备份整个博客目录（除了public和.git）
            for item in Config.BLOG_ROOT_PATH.iterdir():
                if item.name not in ["public", ".git", "backups"] and \
                   (request.include_generated or item.name != "public"):
                    if item.is_dir():
                        shutil.copytree(item, backup_dir / item.name, ignore=shutil.ignore_patterns('*.pyc', '__pycache__'))
                    else:
                        shutil.copy2(item, backup_dir)
        
        elif request.backup_type == "content_only":
            # 只备份内容目录
            shutil.copytree(Config.BLOG_CONTENT_PATH, backup_dir / "content")
            shutil.copytree(Config.BLOG_STATIC_PATH, backup_dir / "static")
        
        elif request.backup_type == "config_only":
            # 只备份配置文件
            config_files = ["config.toml", "pyproject.toml", ".env"]
            for config_file in config_files:
                config_path = Config.BLOG_ROOT_PATH / config_file
                if config_path.exists():
                    shutil.copy2(config_path, backup_dir)
        
        # 压缩备份（如果启用）
        if request.compression:
            archive_path = backup_dir.with_suffix('.tar.gz')
            shutil.make_archive(str(backup_dir), 'gztar', backup_dir.parent, backup_dir.name)
            shutil.rmtree(backup_dir)  # 删除未压缩的目录
            final_path = archive_path
        else:
            final_path = backup_dir
        
        result = {
            "backup_type": request.backup_type,
            "backup_path": str(final_path),
            "backup_size": _get_size(final_path),
            "compressed": request.compression,
            "created_at": datetime.now().isoformat()
        }
        
        logger.info(f"博客备份完成: {final_path}")
        return result
        
    except Exception as e:
        logger.error(f"备份博客时出错: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def analyze_site(request: SiteAnalysisRequest) -> Dict[str, Any]:
    """
    分析网站
    
    Args:
        request: 分析请求
        
    Returns:
        分析结果
    """
    try:
        logger.info(f"开始分析网站: {request.analysis_type}")
        
        if request.analysis_type == "overview":
            result = await _analyze_site_overview()
        elif request.analysis_type == "content":
            result = await _analyze_content()
        elif request.analysis_type == "performance":
            result = await _analyze_performance()
        elif request.analysis_type == "seo":
            result = await _analyze_seo()
        else:
            return {"error": f"不支持的分析类型: {request.analysis_type}"}
        
        result["analysis_type"] = request.analysis_type
        result["analyzed_at"] = datetime.now().isoformat()
        
        logger.info(f"网站分析完成: {request.analysis_type}")
        return result
        
    except Exception as e:
        logger.error(f"分析网站时出错: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def manage_static_files(action: str, file_path: str, target_path: Optional[str] = None) -> Dict[str, Any]:
    """
    管理静态文件
    
    Args:
        action: 操作类型 (copy, move, delete, info)
        file_path: 源文件路径
        target_path: 目标路径（用于copy和move操作）
        
    Returns:
        操作结果
    """
    try:
        logger.info(f"执行静态文件操作: {action} - {file_path}")
        
        source_path = Path(file_path)
        
        if action == "info":
            if not source_path.exists():
                return {"error": "文件不存在"}
            
            stat = source_path.stat()
            result = {
                "file_path": str(source_path),
                "file_size": stat.st_size,
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "is_directory": source_path.is_dir()
            }
            
            if source_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                # 获取图片信息
                try:
                    from PIL import Image
                    with Image.open(source_path) as img:
                        result["image_info"] = {
                            "dimensions": img.size,
                            "format": img.format,
                            "mode": img.mode
                        }
                except:
                    pass
        
        elif action == "copy":
            if not target_path:
                return {"error": "复制操作需要目标路径"}
            
            target = Path(target_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            
            if source_path.is_dir():
                shutil.copytree(source_path, target)
            else:
                shutil.copy2(source_path, target)
            
            result = {
                "action": "copy",
                "source": str(source_path),
                "target": str(target),
                "success": True
            }
        
        elif action == "move":
            if not target_path:
                return {"error": "移动操作需要目标路径"}
            
            target = Path(target_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source_path), str(target))
            
            result = {
                "action": "move",
                "source": str(source_path),
                "target": str(target),
                "success": True
            }
        
        elif action == "delete":
            if source_path.is_dir():
                shutil.rmtree(source_path)
            else:
                source_path.unlink()
            
            result = {
                "action": "delete",
                "path": str(source_path),
                "success": True
            }
        
        else:
            return {"error": f"不支持的操作: {action}"}
        
        logger.info(f"静态文件操作完成: {action}")
        return result
        
    except Exception as e:
        logger.error(f"管理静态文件时出错: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def get_blog_statistics() -> Dict[str, Any]:
    """
    获取博客统计信息
    
    Returns:
        统计信息
    """
    try:
        logger.info("获取博客统计信息")
        
        # 获取博文列表
        posts = zola_utils.get_blog_posts()
        
        # 统计分类和标签
        categories = zola_utils.get_categories()
        tags = zola_utils.get_tags()
        
        # 计算统计数据
        total_posts = len(posts)
        total_words = 0
        posts_by_year = {}
        posts_by_category = {}
        
        for post in posts:
            # 统计年份
            if post.get("date"):
                year = post["date"][:4]
                posts_by_year[year] = posts_by_year.get(year, 0) + 1
            
            # 统计分类
            for category in post.get("category", []):
                posts_by_category[category] = posts_by_category.get(category, 0) + 1
            
            # 统计字数（简单估算）
            if post.get("file_path"):
                try:
                    content = Path(post["file_path"]).read_text(encoding='utf-8')
                    # 简单的字数统计
                    total_words += len(content.split())
                except:
                    pass
        
        # 获取最近的博文
        recent_posts = posts[:5]  # 前5篇最新的博文
        
        result = {
            "total_posts": total_posts,
            "total_categories": len(categories),
            "total_tags": len(tags),
            "estimated_total_words": total_words,
            "posts_by_year": posts_by_year,
            "posts_by_category": posts_by_category,
            "recent_posts": [
                {
                    "title": post.get("title", ""),
                    "date": post.get("date", ""),
                    "category": post.get("category", [])
                } for post in recent_posts
            ],
            "categories": categories,
            "tags": tags,
            "generated_at": datetime.now().isoformat()
        }
        
        logger.info("博客统计信息获取完成")
        return result
        
    except Exception as e:
        logger.error(f"获取博客统计信息时出错: {str(e)}")
        return {"error": str(e)}

async def _deploy_site(commit_message: str) -> Dict[str, Any]:
    """部署网站到GitHub Pages"""
    try:
        # 这里实现Git提交和推送逻辑
        commands = [
            ["git", "add", "."],
            ["git", "commit", "-m", commit_message],
            ["git", "push", "origin", "main"]
        ]
        
        results = []
        for cmd in commands:
            result = subprocess.run(
                cmd,
                cwd=Config.BLOG_ROOT_PATH,
                capture_output=True,
                text=True
            )
            results.append({
                "command": " ".join(cmd),
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            })
            
            if result.returncode != 0:
                break
        
        success = all(r["success"] for r in results)
        
        return {
            "success": success,
            "commit_message": commit_message,
            "commands": results
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def _get_build_stats(public_dir: Path) -> Dict[str, Any]:
    """获取构建统计信息"""
    stats = {
        "total_files": 0,
        "total_size": 0,
        "file_types": {}
    }
    
    for file_path in public_dir.rglob("*"):
        if file_path.is_file():
            stats["total_files"] += 1
            stats["total_size"] += file_path.stat().st_size
            
            suffix = file_path.suffix.lower()
            stats["file_types"][suffix] = stats["file_types"].get(suffix, 0) + 1
    
    stats["total_size_mb"] = round(stats["total_size"] / (1024 * 1024), 2)
    
    return {"build_stats": stats}

def _get_size(path: Path) -> str:
    """获取文件或目录大小的可读格式"""
    if path.is_file():
        size = path.stat().st_size
    else:
        size = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

async def _analyze_site_overview() -> Dict[str, Any]:
    """分析网站概览"""
    # 获取基本统计
    stats = await get_blog_statistics()
    
    # 获取构建信息
    public_dir = Config.BLOG_ROOT_PATH / "public"
    build_stats = _get_build_stats(public_dir) if public_dir.exists() else {}
    
    return {
        "blog_stats": stats,
        "build_info": build_stats,
        "last_build": datetime.fromtimestamp(public_dir.stat().st_mtime).isoformat() if public_dir.exists() else None
    }

async def _analyze_content() -> Dict[str, Any]:
    """分析内容质量"""
    posts = zola_utils.get_blog_posts()
    
    analysis = {
        "total_posts": len(posts),
        "posts_without_summary": 0,
        "posts_without_tags": 0,
        "short_posts": 0,  # 少于500字
        "long_posts": 0,   # 超过3000字
        "orphaned_images": []
    }
    
    for post in posts:
        if not post.get("summary"):
            analysis["posts_without_summary"] += 1
        
        if not post.get("tags"):
            analysis["posts_without_tags"] += 1
        
        # 简单的字数分析
        try:
            if post.get("file_path"):
                content = Path(post["file_path"]).read_text(encoding='utf-8')
                word_count = len(content.split())
                if word_count < 500:
                    analysis["short_posts"] += 1
                elif word_count > 3000:
                    analysis["long_posts"] += 1
        except:
            pass
    
    return analysis

async def _analyze_performance() -> Dict[str, Any]:
    """分析性能"""
    public_dir = Config.BLOG_ROOT_PATH / "public"
    
    if not public_dir.exists():
        return {"error": "网站未构建"}
    
    analysis = {
        "large_files": [],
        "optimization_suggestions": []
    }
    
    # 查找大文件
    for file_path in public_dir.rglob("*"):
        if file_path.is_file():
            size = file_path.stat().st_size
            if size > 1024 * 1024:  # 超过1MB
                analysis["large_files"].append({
                    "path": str(file_path.relative_to(public_dir)),
                    "size": _get_size(file_path)
                })
    
    # 生成优化建议
    if analysis["large_files"]:
        analysis["optimization_suggestions"].append("考虑压缩大文件以提高加载速度")
    
    return analysis

async def _analyze_seo() -> Dict[str, Any]:
    """分析SEO"""
    posts = zola_utils.get_blog_posts()
    
    analysis = {
        "posts_without_meta_description": 0,
        "duplicate_titles": [],
        "missing_alt_text": 0,
        "seo_score": 0
    }
    
    titles = {}
    for post in posts:
        title = post.get("title", "")
        if title in titles:
            analysis["duplicate_titles"].append(title)
        titles[title] = titles.get(title, 0) + 1
        
        if not post.get("summary"):
            analysis["posts_without_meta_description"] += 1
    
    # 计算SEO评分
    total_posts = len(posts)
    if total_posts > 0:
        score = 100
        score -= (analysis["posts_without_meta_description"] / total_posts) * 30
        score -= len(analysis["duplicate_titles"]) * 10
        analysis["seo_score"] = max(0, round(score))
    
    return analysis

def main():
    """主函数，启动 MCP 服务器"""
    try:
        # 验证配置
        Config.validate()
        logger.info("博客管理服务器启动中...")
        mcp.run()
    except Exception as e:
        logger.error(f"启动服务器时出错: {str(e)}")
        raise

if __name__ == "__main__":
    main()
