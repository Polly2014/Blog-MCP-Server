"""
Zola 工具模块
提供 Zola 博客系统相关的工具函数
"""
import re
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import frontmatter
import logging

from ..config import Config

logger = logging.getLogger(__name__)

class ZolaUtils:
    """Zola 工具类"""
    
    def __init__(self):
        self.blog_root = Config.BLOG_ROOT_PATH
        self.content_path = Config.BLOG_CONTENT_PATH
        self.static_path = Config.BLOG_STATIC_PATH
    
    def generate_frontmatter(
        self,
        title: str,
        category: str = "技术",
        tags: List[str] = None,
        summary: str = "",
        template: str = "blog.html",
        date: Optional[str] = None
    ) -> str:
        """
        生成 Zola frontmatter
        
        Args:
            title: 文章标题
            category: 文章分类
            tags: 标签列表
            summary: 文章摘要
            template: 模板名称
            date: 发布日期
            
        Returns:
            格式化的 frontmatter 字符串
        """
        if tags is None:
            tags = []
        
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        slug = self.generate_slug(title)
        
        frontmatter_data = {
            "title": title,
            "date": date,
            "template": template,
            "slug": slug,
            "path": slug,
            "archive": [str(datetime.now().year)],
            "taxonomies": {
                "category": [category],
                "tags": tags
            },
            "extra": {
                "author": "Polly",
                "summary": summary
            }
        }
        
        # 转换为 TOML 格式的 frontmatter
        toml_content = self._dict_to_toml(frontmatter_data)
        
        return f"+++\n{toml_content}+++"
    
    def generate_slug(self, title: str) -> str:
        """
        生成 URL slug
        
        Args:
            title: 文章标题
            
        Returns:
            URL slug
        """
        # 移除特殊字符，保留中文字符
        slug = re.sub(r'[^\w\s\-\u4e00-\u9fff]', '', title)
        # 替换空格为连字符
        slug = re.sub(r'[\s]+', '-', slug)
        # 转换为小写（保留中文）
        slug = slug.lower()
        # 移除多余的连字符
        slug = re.sub(r'-+', '-', slug)
        # 移除首尾连字符
        slug = slug.strip('-')
        
        # 如果是纯中文，转换为拼音或使用英文翻译
        if re.match(r'^[\u4e00-\u9fff\-]+$', slug):
            # 简单处理：提取关键词
            slug = self._chinese_to_slug(title)
        
        return slug
    
    def _chinese_to_slug(self, title: str) -> str:
        """
        将中文标题转换为英文 slug
        这里简化处理，实际项目中可以使用 pypinyin 等库
        """
        # 简单的中文关键词映射
        keyword_map = {
            "AI": "ai",
            "人工智能": "artificial-intelligence",
            "机器学习": "machine-learning",
            "深度学习": "deep-learning",
            "博客": "blog",
            "教程": "tutorial",
            "指南": "guide",
            "实践": "practice",
            "技术": "technology",
            "开发": "development",
            "编程": "programming",
            "代码": "code",
            "项目": "project",
            "工具": "tools",
            "框架": "framework",
            "部署": "deployment",
            "优化": "optimization",
            "分析": "analysis",
            "设计": "design",
            "客栈": "guesthouse",
            "丽江": "lijiang"
        }
        
        slug_parts = []
        for keyword, english in keyword_map.items():
            if keyword in title:
                slug_parts.append(english)
        
        if not slug_parts:
            # 如果没有匹配的关键词，使用日期
            return f"post-{datetime.now().strftime('%Y%m%d')}"
        
        return "-".join(slug_parts[:3])  # 最多取3个关键词
    
    def _dict_to_toml(self, data: dict, level: int = 0) -> str:
        """
        将字典转换为 TOML 格式字符串
        
        Args:
            data: 要转换的字典
            level: 嵌套级别
            
        Returns:
            TOML 格式字符串
        """
        toml_lines = []
        indent = "  " * level
        
        for key, value in data.items():
            if isinstance(value, dict):
                toml_lines.append(f"{indent}[{key}]")
                toml_lines.append(self._dict_to_toml(value, level + 1))
            elif isinstance(value, list):
                if value and isinstance(value[0], str):
                    # 字符串列表
                    formatted_list = ", ".join(f'"{item}"' for item in value)
                    toml_lines.append(f'{indent}{key} = [{formatted_list}]')
                else:
                    # 其他类型的列表
                    toml_lines.append(f'{indent}{key} = {value}')
            elif isinstance(value, str):
                # 字符串值需要加引号
                toml_lines.append(f'{indent}{key} = "{value}"')
            else:
                # 其他类型（数字、布尔值等）
                toml_lines.append(f'{indent}{key} = {value}')
        
        return "\n".join(toml_lines) + "\n"
    
    def parse_frontmatter(self, file_path: str) -> Dict[str, Any]:
        """
        解析文件的 frontmatter
        
        Args:
            file_path: 文件路径
            
        Returns:
            解析后的 frontmatter 数据
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
                return post.metadata
        except Exception as e:
            logger.error(f"解析 frontmatter 时出错: {str(e)}")
            return {}
    
    def get_blog_posts(self) -> List[Dict[str, Any]]:
        """
        获取所有博文列表
        
        Returns:
            博文信息列表
        """
        posts = []
        blog_dir = self.content_path / "blog"
        
        if not blog_dir.exists():
            return posts
        
        for file_path in blog_dir.glob("*.md"):
            try:
                metadata = self.parse_frontmatter(str(file_path))
                posts.append({
                    "file_path": str(file_path),
                    "title": metadata.get("title", file_path.stem),
                    "date": metadata.get("date"),
                    "category": metadata.get("taxonomies", {}).get("category", []),
                    "tags": metadata.get("taxonomies", {}).get("tags", []),
                    "summary": metadata.get("extra", {}).get("summary", "")
                })
            except Exception as e:
                logger.error(f"处理文件 {file_path} 时出错: {str(e)}")
                continue
        
        # 按日期排序
        posts.sort(key=lambda x: x.get("date", ""), reverse=True)
        return posts
    
    def get_categories(self) -> List[str]:
        """
        获取所有分类
        
        Returns:
            分类列表
        """
        categories = set()
        posts = self.get_blog_posts()
        
        for post in posts:
            categories.update(post.get("category", []))
        
        return sorted(list(categories))
    
    def get_tags(self) -> List[str]:
        """
        获取所有标签
        
        Returns:
            标签列表
        """
        tags = set()
        posts = self.get_blog_posts()
        
        for post in posts:
            tags.update(post.get("tags", []))
        
        return sorted(list(tags))
    
    def build_site(self) -> Dict[str, Any]:
        """
        构建 Zola 网站
        
        Returns:
            构建结果
        """
        try:
            import subprocess
            
            # 切换到博客根目录
            result = subprocess.run(
                ["zola", "build"],
                cwd=self.blog_root,
                capture_output=True,
                text=True
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
            
        except Exception as e:
            logger.error(f"构建网站时出错: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def serve_site(self, port: int = 1111) -> Dict[str, Any]:
        """
        启动 Zola 开发服务器
        
        Args:
            port: 服务器端口
            
        Returns:
            启动结果
        """
        try:
            import subprocess
            
            # 启动开发服务器（后台运行）
            process = subprocess.Popen(
                ["zola", "serve", "--port", str(port)],
                cwd=self.blog_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            return {
                "success": True,
                "process_id": process.pid,
                "url": f"http://localhost:{port}",
                "message": f"开发服务器已启动，访问 http://localhost:{port}"
            }
            
        except Exception as e:
            logger.error(f"启动开发服务器时出错: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def validate_content(self, content: str) -> Dict[str, Any]:
        """
        验证内容格式
        
        Args:
            content: 博文内容
            
        Returns:
            验证结果
        """
        issues = []
        warnings = []
        
        # 检查是否有 frontmatter
        if not content.startswith("+++"):
            issues.append("缺少 frontmatter")
        
        # 检查 Markdown 格式
        if "# " not in content and "## " not in content:
            warnings.append("建议添加标题结构")
        
        # 检查图片链接
        image_links = re.findall(r'!\[.*?\]\((.*?)\)', content)
        for link in image_links:
            if link.startswith("http"):
                warnings.append(f"外部图片链接: {link}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "image_count": len(image_links),
            "word_count": len(content.split())
        }
