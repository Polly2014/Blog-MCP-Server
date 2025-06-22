"""
内容服务模块
提供博文内容生成、优化和分析功能
"""
import re
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from .ai_service import AIService

logger = logging.getLogger(__name__)

class ContentService:
    """内容服务类"""
    
    def __init__(self):
        self.ai_service = AIService()
    
    async def generate_blog_content(
        self, 
        topic: str, 
        outline: Optional[str] = None,
        style: str = "professional",
        target_length: str = "medium",
        include_code: bool = True
    ) -> Dict[str, Any]:
        """
        生成博文内容
        
        Args:
            topic: 博文主题
            outline: 可选的大纲
            style: 写作风格
            target_length: 目标长度
            include_code: 是否包含代码示例
            
        Returns:
            生成的博文内容字典
        """
        try:
            # 构建提示词
            prompt = self._build_content_prompt(topic, outline, style, target_length, include_code)
            
            # 调用 AI 服务生成内容
            response = await self.ai_service.generate_text(prompt)
            
            # 解析响应
            content_data = self._parse_content_response(response)
            
            return content_data
            
        except Exception as e:
            logger.error(f"生成博文内容时出错: {str(e)}")
            raise
    
    async def optimize_content(
        self, 
        content: str, 
        optimization_type: str = "seo",
        keywords: List[str] = []
    ) -> Dict[str, Any]:
        """
        优化博文内容
        
        Args:
            content: 原始内容
            optimization_type: 优化类型 (seo, readability, engagement)
            keywords: 目标关键词
            
        Returns:
            优化后的内容和改进建议
        """
        try:
            prompt = self._build_optimization_prompt(content, optimization_type, keywords)
            
            response = await self.ai_service.generate_text(prompt)
            
            optimization_data = self._parse_optimization_response(response)
            
            return optimization_data
            
        except Exception as e:
            logger.error(f"优化内容时出错: {str(e)}")
            raise
    
    async def generate_outline(self, topic: str, depth: str = "medium") -> Dict[str, Any]:
        """
        生成博文大纲
        
        Args:
            topic: 博文主题
            depth: 大纲深度
            
        Returns:
            生成的大纲结构
        """
        try:
            prompt = self._build_outline_prompt(topic, depth)
            
            response = await self.ai_service.generate_text(prompt)
            
            outline_data = self._parse_outline_response(response)
            
            return outline_data
            
        except Exception as e:
            logger.error(f"生成大纲时出错: {str(e)}")
            raise
    
    def suggest_image_positions(self, content: str) -> List[Dict[str, Any]]:
        """
        建议图片插入位置
        
        Args:
            content: 博文内容
            
        Returns:
            图片位置建议列表
        """
        suggestions = []
        
        # 查找标题位置
        headers = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
        
        for i, (level, title) in enumerate(headers):
            # 在每个二级标题后建议插入图片
            if level == "##":
                suggestions.append({
                    "position": f"after_header_{i}",
                    "title": title,
                    "suggestion": f"在'{title}'段落后插入相关图片",
                    "image_type": "illustration",
                    "priority": "medium"
                })
        
        # 在文章开头建议插入封面图
        suggestions.insert(0, {
            "position": "cover",
            "title": "封面图片",
            "suggestion": "在文章开头插入引人注目的封面图片",
            "image_type": "cover",
            "priority": "high"
        })
        
        return suggestions
    
    def estimate_reading_time(self, content: str) -> int:
        """
        估算阅读时间（分钟）
        
        Args:
            content: 博文内容
            
        Returns:
            估算的阅读时间（分钟）
        """
        # 移除 Markdown 标记
        text = re.sub(r'[#*`\[\]()]', '', content)
        word_count = len(text.split())
        
        # 假设每分钟阅读 200 个单词
        reading_time = max(1, round(word_count / 200))
        
        return reading_time
    
    async def analyze_content_performance(self, content: str) -> Dict[str, Any]:
        """
        分析内容性能
        
        Args:
            content: 博文内容
            
        Returns:
            性能分析结果
        """
        try:
            # 基本统计
            word_count = len(content.split())
            reading_time = self.estimate_reading_time(content)
            
            # 调用 AI 进行深度分析
            analysis_prompt = f"""
            请分析以下博文内容的性能指标，并给出评分（1-10分）和改进建议：
            
            内容：
            {content[:2000]}...
            
            请从以下方面分析：
            1. SEO优化程度
            2. 可读性
            3. 参与度潜力
            4. 改进建议
            
            返回JSON格式的分析结果。
            """
            
            analysis_response = await self.ai_service.generate_text(analysis_prompt)
            analysis_data = self._parse_analysis_response(analysis_response)
            
            return {
                "word_count": word_count,
                "reading_time": reading_time,
                "seo_score": analysis_data.get("seo_score", 7),
                "readability_score": analysis_data.get("readability_score", 7),
                "engagement_potential": analysis_data.get("engagement_potential", 7),
                "suggestions": analysis_data.get("suggestions", [])
            }
            
        except Exception as e:
            logger.error(f"分析内容性能时出错: {str(e)}")
            # 返回基本分析
            return {
                "word_count": len(content.split()),
                "reading_time": self.estimate_reading_time(content),
                "seo_score": 7,
                "readability_score": 7,
                "engagement_potential": 7,
                "suggestions": ["建议添加更多小标题", "考虑增加代码示例", "添加相关图片"]
            }
    
    def _build_content_prompt(
        self, 
        topic: str, 
        outline: Optional[str], 
        style: str, 
        target_length: str,
        include_code: bool
    ) -> str:
        """构建内容生成提示词"""
        
        length_map = {
            "short": "800-1200字",
            "medium": "1500-2500字",
            "long": "3000-5000字"
        }
        
        style_map = {
            "professional": "专业技术风格，适当使用技术术语",
            "casual": "轻松友好的风格，易于理解",
            "academic": "学术严谨的风格，引用相关研究"
        }
        
        prompt = f"""
你是Polly的博文写作助手。请根据以下要求创作一篇高质量的技术博文：

**主题**: {topic}

**写作要求**:
- 风格: {style_map.get(style, style)}
- 长度: {length_map.get(target_length, target_length)}
- 使用第一人称叙述
- 保持专业但亲切的语调
"""

        if outline:
            prompt += f"\n**参考大纲**:\n{outline}\n"
        
        if include_code:
            prompt += "\n- 包含相关的代码示例和技术细节"
        
        prompt += """

**输出格式**:
请返回JSON格式，包含以下字段：
{
    "title": "博文标题",
    "summary": "简短摘要（100-150字）",
    "content": "完整的博文内容（Markdown格式）"
}

博文内容应该包含：
1. 引人入胜的开头
2. 清晰的章节结构
3. 实用的技术洞察
4. 个人经验和观点
5. 总结和展望

请确保内容原创、有价值，能够为读者提供实用的技术知识和见解。
"""
        
        return prompt
    
    def _build_optimization_prompt(self, content: str, optimization_type: str, keywords: List[str]) -> str:
        """构建内容优化提示词"""
        
        optimization_types = {
            "seo": "搜索引擎优化，提高关键词密度和结构",
            "readability": "提高可读性，改善句式结构和表达",
            "engagement": "提高参与度，增加互动元素和吸引力"
        }
        
        prompt = f"""
请优化以下博文内容，优化类型: {optimization_types.get(optimization_type, optimization_type)}

原始内容:
{content[:3000]}...

"""
        
        if keywords:
            prompt += f"目标关键词: {', '.join(keywords)}\n"
        
        prompt += """
请返回JSON格式的优化结果：
{
    "content": "优化后的内容",
    "improvements": ["改进点1", "改进点2", ...],
    "seo_score": 评分(1-10),
    "readability_score": 评分(1-10)
}
"""
        
        return prompt
    
    def _build_outline_prompt(self, topic: str, depth: str) -> str:
        """构建大纲生成提示词"""
        
        depth_map = {
            "shallow": "简要大纲，3-5个主要点",
            "medium": "中等深度，5-8个主要点，每个包含2-3个子点",
            "deep": "详细大纲，8-12个主要点，多层次结构"
        }
        
        prompt = f"""
请为主题"{topic}"生成一个技术博文的详细大纲。

要求: {depth_map.get(depth, depth)}

请返回JSON格式：
{{
    "structure": [
        {{
            "title": "章节标题",
            "description": "章节描述",
            "subsections": ["子章节1", "子章节2", ...]
        }}
    ],
    "estimated_length": "预估字数",
    "key_points": ["关键点1", "关键点2", ...],
    "resources": ["建议的参考资源"]
}}
"""
        
        return prompt
    
    def _parse_content_response(self, response: str) -> Dict[str, Any]:
        """解析内容生成响应"""
        try:
            import json
            return json.loads(response)
        except:
            # 如果解析失败，返回基本结构
            return {
                "title": "生成的博文",
                "summary": "博文摘要",
                "content": response
            }
    
    def _parse_optimization_response(self, response: str) -> Dict[str, Any]:
        """解析优化响应"""
        try:
            import json
            return json.loads(response)
        except:
            return {
                "content": response,
                "improvements": ["内容已优化"],
                "seo_score": 8,
                "readability_score": 8
            }
    
    def _parse_outline_response(self, response: str) -> Dict[str, Any]:
        """解析大纲响应"""
        try:
            import json
            return json.loads(response)
        except:
            return {
                "structure": [{"title": "主要内容", "description": "大纲内容", "subsections": []}],
                "estimated_length": "2000字",
                "key_points": ["要点1", "要点2"],
                "resources": []
            }
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """解析分析响应"""
        try:
            import json
            return json.loads(response)
        except:
            return {
                "seo_score": 7,
                "readability_score": 7,
                "engagement_potential": 7,
                "suggestions": ["增加小标题", "添加代码示例"]
            }
