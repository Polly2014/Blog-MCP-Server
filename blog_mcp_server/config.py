"""
配置管理模块
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """配置类，管理所有环境变量和配置项"""
    
    # Azure OpenAI 配置
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "dall-e-3")
    
    # DeepSeek 配置
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    
    # OpenAI 配置
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # 博客路径配置
    BLOG_ROOT_PATH = Path(os.getenv("BLOG_ROOT_PATH", "/Users/polly/Downloads/Sublime_Workspace/Zola_Workspace/www.polly.com"))
    BLOG_CONTENT_PATH = Path(os.getenv("BLOG_CONTENT_PATH", BLOG_ROOT_PATH / "content"))
    BLOG_STATIC_PATH = Path(os.getenv("BLOG_STATIC_PATH", BLOG_ROOT_PATH / "static"))
    
    # 输出配置
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output/images")
    IMAGE_SIZE = os.getenv("IMAGE_SIZE", "1792x1024")
    IMAGE_QUALITY = os.getenv("IMAGE_QUALITY", "standard")
    
    # 处理配置
    API_DELAY = int(os.getenv("API_DELAY", "2"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    
    # 调试配置
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls):
        """验证必要的配置项是否存在"""
        required_vars = []
        
        if not cls.AZURE_OPENAI_API_KEY and not cls.OPENAI_API_KEY:
            required_vars.append("AZURE_OPENAI_API_KEY or OPENAI_API_KEY")
        
        if required_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(required_vars)}")
        
        return True
