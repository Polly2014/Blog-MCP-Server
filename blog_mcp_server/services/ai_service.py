"""
AI 服务模块
提供与各种 AI API 的集成
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
import httpx
from openai import AsyncOpenAI
try:
    from openai import AsyncAzureOpenAI
except ImportError:
    AsyncAzureOpenAI = None
import base64
import io

from ..config import Config

logger = logging.getLogger(__name__)

class AIService:
    """AI 服务类，集成多个 AI 提供商"""
    
    def __init__(self):
        self.openai_client = None
        self.azure_client = None
        self._init_clients()
    
    def _init_clients(self):
        """初始化 AI 客户端"""
        try:
            # 初始化 OpenAI 客户端
            if Config.OPENAI_API_KEY:
                self.openai_client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
            
            # 初始化 Azure OpenAI 客户端
            if Config.AZURE_OPENAI_API_KEY and Config.AZURE_OPENAI_ENDPOINT and AsyncAzureOpenAI:
                self.azure_client = AsyncAzureOpenAI(
                    api_key=Config.AZURE_OPENAI_API_KEY,
                    azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
                    api_version="2024-02-15-preview"
                )
            elif Config.AZURE_OPENAI_API_KEY and Config.AZURE_OPENAI_ENDPOINT:
                # 使用标准 OpenAI 客户端作为备选
                self.azure_client = AsyncOpenAI(
                    api_key=Config.AZURE_OPENAI_API_KEY,
                    base_url=f"{Config.AZURE_OPENAI_ENDPOINT}/openai/deployments"
                )
                
            logger.info("AI 客户端初始化完成")
            
        except Exception as e:
            logger.error(f"初始化 AI 客户端时出错: {str(e)}")
    
    async def generate_text(
        self, 
        prompt: str, 
        model: str = "deepseek",
        max_tokens: int = 4000,
        temperature: float = 0.7
    ) -> str:
        """
        生成文本内容
        
        Args:
            prompt: 输入提示词
            model: 使用的模型 (deepseek, gpt-4, gpt-3.5-turbo)
            max_tokens: 最大令牌数
            temperature: 温度参数
            
        Returns:
            生成的文本内容
        """
        try:
            if model == "deepseek":
                return await self._generate_with_deepseek(prompt, max_tokens, temperature)
            elif model.startswith("gpt"):
                return await self._generate_with_openai(prompt, model, max_tokens, temperature)
            else:
                # 默认使用 DeepSeek
                return await self._generate_with_deepseek(prompt, max_tokens, temperature)
                
        except Exception as e:
            logger.error(f"生成文本时出错: {str(e)}")
            raise
    
    async def generate_image(
        self, 
        prompt: str, 
        size: str = "1792x1024",
        quality: str = "standard",
        model: str = "dall-e-3"
    ) -> Dict[str, Any]:
        """
        生成图片
        
        Args:
            prompt: 图片描述提示词
            size: 图片尺寸
            quality: 图片质量
            model: 使用的模型
            
        Returns:
            包含图片URL或数据的字典
        """
        try:
            if self.azure_client:
                return await self._generate_image_with_azure(prompt, size, quality, model)
            elif self.openai_client:
                return await self._generate_image_with_openai(prompt, size, quality, model)
            else:
                raise ValueError("没有可用的图片生成服务")
                
        except Exception as e:
            logger.error(f"生成图片时出错: {str(e)}")
            raise
    
    async def _generate_with_deepseek(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """使用 DeepSeek API 生成文本"""
        if not Config.DEEPSEEK_API_KEY:
            raise ValueError("DeepSeek API 密钥未配置")
        
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {Config.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
    
    async def _generate_with_openai(self, prompt: str, model: str, max_tokens: int, temperature: float) -> str:
        """使用 OpenAI API 生成文本"""
        if not self.openai_client:
            raise ValueError("OpenAI 客户端未初始化")
        
        response = await self.openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.choices[0].message.content
    
    async def _generate_image_with_azure(self, prompt: str, size: str, quality: str, model: str) -> Dict[str, Any]:
        """使用 Azure OpenAI 生成图片"""
        if not self.azure_client:
            raise ValueError("Azure OpenAI 客户端未初始化")
        
        response = await self.azure_client.images.generate(
            model=Config.AZURE_OPENAI_DEPLOYMENT,
            prompt=prompt,
            size=size,
            quality=quality,
            n=1
        )
        
        return {
            "url": response.data[0].url,
            "revised_prompt": response.data[0].revised_prompt
        }
    
    async def _generate_image_with_openai(self, prompt: str, size: str, quality: str, model: str) -> Dict[str, Any]:
        """使用 OpenAI 生成图片"""
        if not self.openai_client:
            raise ValueError("OpenAI 客户端未初始化")
        
        response = await self.openai_client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            quality=quality,
            n=1
        )
        
        return {
            "url": response.data[0].url,
            "revised_prompt": getattr(response.data[0], 'revised_prompt', prompt)
        }
    
    async def analyze_image(self, image_url: str, query: str = "描述这张图片") -> str:
        """
        分析图片内容
        
        Args:
            image_url: 图片URL
            query: 分析查询
            
        Returns:
            图片分析结果
        """
        try:
            if self.openai_client:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4-vision-preview",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": query},
                                {"type": "image_url", "image_url": {"url": image_url}}
                            ]
                        }
                    ],
                    max_tokens=1000
                )
                return response.choices[0].message.content
            else:
                raise ValueError("图片分析需要 OpenAI 客户端")
                
        except Exception as e:
            logger.error(f"分析图片时出错: {str(e)}")
            raise
    
    async def translate_text(self, text: str, target_language: str = "en") -> str:
        """
        翻译文本
        
        Args:
            text: 要翻译的文本
            target_language: 目标语言代码
            
        Returns:
            翻译后的文本
        """
        try:
            prompt = f"请将以下文本翻译成{target_language}语言，保持原意和风格：\n\n{text}"
            return await self.generate_text(prompt, temperature=0.3)
            
        except Exception as e:
            logger.error(f"翻译文本时出错: {str(e)}")
            raise
    
    async def summarize_text(self, text: str, max_length: int = 200) -> str:
        """
        总结文本
        
        Args:
            text: 要总结的文本
            max_length: 总结的最大长度
            
        Returns:
            文本总结
        """
        try:
            prompt = f"请将以下文本总结为不超过{max_length}字的摘要：\n\n{text}"
            return await self.generate_text(prompt, temperature=0.3)
            
        except Exception as e:
            logger.error(f"总结文本时出错: {str(e)}")
            raise
    
    async def enhance_prompt(self, basic_prompt: str, style: str = "detailed") -> str:
        """
        优化提示词
        
        Args:
            basic_prompt: 基础提示词
            style: 优化风格 (detailed, creative, technical)
            
        Returns:
            优化后的提示词
        """
        try:
            enhancement_prompt = f"""
请优化以下提示词，使其更加{style}和有效：

原始提示词：{basic_prompt}

请返回优化后的提示词，要求：
1. 更清晰的指令
2. 更具体的描述
3. 更好的结构
4. 适合AI理解和执行

优化后的提示词：
"""
            return await self.generate_text(enhancement_prompt, temperature=0.5)
            
        except Exception as e:
            logger.error(f"优化提示词时出错: {str(e)}")
            raise
