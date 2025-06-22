"""
丽江客栈管理 MCP 服务器
提供客栈设计、营销文案、文化元素整合等功能
"""
import asyncio
import logging
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
mcp = FastMCP("Lijiang Guesthouse Server")

# 初始化服务
ai_service = AIService()
zola_utils = ZolaUtils()

class GuesthouseDesignRequest(BaseModel):
    """客栈设计请求模型"""
    space_type: str  # 大堂、客房、露台、庭院等
    style: str = "traditional"  # traditional, modern, fusion
    size: str = "medium"  # small, medium, large
    special_requirements: List[str] = []
    cultural_elements: List[str] = ["纳西族", "东巴文化"]
    budget_range: str = "medium"  # low, medium, high

class MarketingContentRequest(BaseModel):
    """营销内容请求模型"""
    content_type: str  # 小红书文案、抖音脚本、微信推文等
    target_audience: str = "年轻游客"
    season: str = "四季通用"
    highlights: List[str] = []
    platform_style: str = "engaging"  # formal, engaging, casual

class CulturalIntegrationRequest(BaseModel):
    """文化元素整合请求模型"""
    element_type: str  # 东巴文字、纳西音乐、传统工艺等
    application_area: str  # 装饰、活动、服务等
    authenticity_level: str = "high"  # low, medium, high
    modern_adaptation: bool = True

@mcp.tool()
async def design_guesthouse_space(request: GuesthouseDesignRequest) -> Dict[str, Any]:
    """
    设计客栈空间方案
    
    Args:
        request: 客栈设计请求，包含空间类型、风格等信息
        
    Returns:
        设计方案详情
    """
    try:
        logger.info(f"开始设计客栈空间: {request.space_type}")
        
        # 构建设计提示词
        prompt = f"""
你是专业的丽江客栈设计师，请为以下空间设计一个详细的方案：

空间类型：{request.space_type}
设计风格：{request.style}
空间大小：{request.size}
特殊要求：{', '.join(request.special_requirements) if request.special_requirements else '无'}
文化元素：{', '.join(request.cultural_elements)}
预算范围：{request.budget_range}

请提供以下内容：
1. 设计理念和主题
2. 空间布局规划
3. 色彩搭配方案
4. 材料选择建议
5. 家具和装饰推荐
6. 灯光设计方案
7. 文化元素融入方式
8. 预算估算
9. 实施建议

请以JSON格式返回详细的设计方案。
"""
        
        # 生成设计方案
        response = await ai_service.generate_text(prompt, model="deepseek", max_tokens=3000)
        
        try:
            import json
            design_data = json.loads(response)
        except:
            # 如果解析失败，创建基本结构
            design_data = {
                "design_concept": "融合传统纳西文化与现代舒适的设计理念",
                "layout": f"{request.space_type}的合理布局规划",
                "color_scheme": "以木色、白色为主，点缀纳西蓝",
                "materials": ["木材", "石材", "传统织物"],
                "furniture": ["纳西风格家具", "现代舒适设施"],
                "lighting": "温暖柔和的照明设计",
                "cultural_integration": "东巴文字装饰，纳西音乐背景",
                "budget_estimate": "根据预算范围提供估算",
                "implementation": "分阶段实施建议",
                "raw_response": response
            }
        
        # 生成DALL-E图片提示词
        image_prompt = await _generate_image_prompt(request, design_data)
        
        result = {
            "space_type": request.space_type,
            "design_data": design_data,
            "image_prompt": image_prompt,
            "cultural_elements": request.cultural_elements,
            "estimated_cost": design_data.get("budget_estimate", "待详细评估"),
            "implementation_timeline": "2-4周",
            "generated_at": datetime.now().isoformat()
        }
        
        logger.info(f"客栈空间设计完成: {request.space_type}")
        return result
        
    except Exception as e:
        logger.error(f"设计客栈空间时出错: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def create_marketing_content(request: MarketingContentRequest) -> Dict[str, Any]:
    """
    创建营销内容
    
    Args:
        request: 营销内容请求
        
    Returns:
        营销内容详情
    """
    try:
        logger.info(f"开始创建营销内容: {request.content_type}")
        
        # 根据平台类型构建不同的提示词
        platform_prompts = {
            "小红书": "创作小红书风格的图文内容，要求有吸引人的标题、精美的配图建议和详细的文案",
            "抖音脚本": "创作抖音短视频脚本，包含分镜头设计、配音文案和拍摄建议",
            "微信推文": "创作微信公众号推文，要求有完整的文章结构和引人入胜的内容",
            "宣传册": "创作客栈宣传册内容，包含客栈介绍、服务特色和文化体验"
        }
        
        base_prompt = platform_prompts.get(request.content_type, "创作营销内容")
        
        prompt = f"""
你是专业的丽江客栈营销专家，请{base_prompt}：

内容类型：{request.content_type}
目标受众：{request.target_audience}
季节特色：{request.season}
亮点特色：{', '.join(request.highlights) if request.highlights else '客栈独特魅力'}
风格要求：{request.platform_style}

请围绕以下主题创作：
- 丽江古城的独特魅力
- 纳西文化的深度体验
- 客栈的温馨舒适
- 玉龙雪山的壮美景色
- 当地特色美食和茶文化

请以JSON格式返回，包含：
1. 标题/主题
2. 主要内容
3. 配图建议
4. 发布建议
5. 预期效果
"""
        
        # 生成营销内容
        response = await ai_service.generate_text(prompt, model="deepseek", max_tokens=2500)
        
        try:
            import json
            content_data = json.loads(response)
        except:
            content_data = {
                "title": f"精彩的{request.content_type}内容",
                "content": response,
                "image_suggestions": ["客栈外观", "客房内景", "丽江古城"],
                "publishing_tips": ["选择最佳发布时间", "使用相关话题标签"],
                "expected_results": "预期获得良好的用户互动和曝光"
            }
        
        result = {
            "content_type": request.content_type,
            "content_data": content_data,
            "target_audience": request.target_audience,
            "platform_optimization": _get_platform_optimization_tips(request.content_type),
            "generated_at": datetime.now().isoformat()
        }
        
        logger.info(f"营销内容创建完成: {request.content_type}")
        return result
        
    except Exception as e:
        logger.error(f"创建营销内容时出错: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def integrate_cultural_elements(request: CulturalIntegrationRequest) -> Dict[str, Any]:
    """
    整合文化元素
    
    Args:
        request: 文化元素整合请求
        
    Returns:
        文化整合方案
    """
    try:
        logger.info(f"开始整合文化元素: {request.element_type}")
        
        prompt = f"""
你是纳西族文化专家和客栈设计顾问，请为客栈文化元素整合提供专业建议：

文化元素：{request.element_type}
应用领域：{request.application_area}
真实性要求：{request.authenticity_level}
现代化改造：{'是' if request.modern_adaptation else '否'}

请提供：
1. 文化元素的历史背景和意义
2. 在客栈中的具体应用方式
3. 现代化改造建议（如适用）
4. 实施的注意事项
5. 文化传承的重要性
6. 游客教育和体验设计
7. 与其他元素的协调搭配

请以JSON格式返回详细方案。
"""
        
        response = await ai_service.generate_text(prompt, model="deepseek", max_tokens=2000)
        
        try:
            import json
            cultural_data = json.loads(response)
        except:
            cultural_data = {
                "background": f"{request.element_type}的历史文化背景",
                "application": f"在{request.application_area}中的应用方式",
                "modernization": "现代化改造建议" if request.modern_adaptation else "传统保持建议",
                "considerations": ["尊重文化传统", "确保表达准确性"],
                "importance": "文化传承的重要价值",
                "experience_design": "游客文化体验设计",
                "coordination": "与其他元素的搭配建议",
                "raw_response": response
            }
        
        result = {
            "element_type": request.element_type,
            "cultural_data": cultural_data,
            "authenticity_guidelines": _get_authenticity_guidelines(request.element_type),
            "implementation_checklist": _get_implementation_checklist(request.element_type),
            "generated_at": datetime.now().isoformat()
        }
        
        logger.info(f"文化元素整合完成: {request.element_type}")
        return result
        
    except Exception as e:
        logger.error(f"整合文化元素时出错: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def generate_activity_plan(
    activity_type: str,
    season: str = "四季通用",
    participant_count: int = 10,
    duration: str = "2小时"
) -> Dict[str, Any]:
    """
    生成客栈活动策划方案
    
    Args:
        activity_type: 活动类型（如茶文化体验、纳西音乐分享会等）
        season: 季节
        participant_count: 参与人数
        duration: 活动时长
        
    Returns:
        活动策划方案
    """
    try:
        logger.info(f"开始生成活动策划: {activity_type}")
        
        prompt = f"""
你是专业的客栈活动策划师，请为以下活动设计详细方案：

活动类型：{activity_type}
适用季节：{season}
参与人数：{participant_count}人
活动时长：{duration}

请提供：
1. 活动主题和目标
2. 详细活动流程
3. 所需物料和设备
4. 空间布置要求
5. 人员配置
6. 预算估算
7. 风险评估和应急预案
8. 效果评估标准

请以JSON格式返回完整的活动策划方案。
"""
        
        response = await ai_service.generate_text(prompt, model="deepseek", max_tokens=2500)
        
        try:
            import json
            activity_data = json.loads(response)
        except:
            activity_data = {
                "theme": f"{activity_type}主题活动",
                "objectives": ["提升客人体验", "传播文化", "增强互动"],
                "schedule": f"{duration}的详细活动流程",
                "materials": ["所需物料清单"],
                "setup": "活动空间布置要求",
                "staff": "人员配置建议",
                "budget": "预算估算",
                "risks": "风险评估",
                "evaluation": "效果评估标准",
                "raw_response": response
            }
        
        result = {
            "activity_type": activity_type,
            "activity_data": activity_data,
            "booking_suggestions": _get_booking_suggestions(activity_type),
            "follow_up_activities": _get_follow_up_activities(activity_type),
            "generated_at": datetime.now().isoformat()
        }
        
        logger.info(f"活动策划生成完成: {activity_type}")
        return result
        
    except Exception as e:
        logger.error(f"生成活动策划时出错: {str(e)}")
        return {"error": str(e)}

async def _generate_image_prompt(request: GuesthouseDesignRequest, design_data: Dict[str, Any]) -> str:
    """生成设计效果图的DALL-E提示词"""
    
    style_keywords = {
        "traditional": "traditional Naxi architecture, wooden structure, traditional Chinese elements",
        "modern": "modern minimalist design, clean lines, contemporary furniture",
        "fusion": "fusion of traditional and modern, harmonious blend of old and new"
    }
    
    prompt = f"""
A beautiful {request.space_type} in a Lijiang guesthouse, {style_keywords.get(request.style, request.style)} style.
Featuring {', '.join(request.cultural_elements)} cultural elements.
Warm lighting, comfortable atmosphere, {request.size} size space.
High quality interior design photography, professional composition.
"""
    
    return prompt

def _get_platform_optimization_tips(content_type: str) -> List[str]:
    """获取平台优化建议"""
    
    tips_map = {
        "小红书": [
            "使用吸引眼球的封面图",
            "添加相关话题标签",
            "在最佳时间发布（晚上7-9点）",
            "鼓励用户互动和分享"
        ],
        "抖音脚本": [
            "前3秒要抓住注意力",
            "使用热门音乐或原创配音",
            "添加字幕提高观看体验",
            "结尾引导关注和点赞"
        ],
        "微信推文": [
            "标题要有吸引力",
            "内容结构清晰",
            "适当使用表情符号",
            "在阅读高峰期发布"
        ]
    }
    
    return tips_map.get(content_type, ["根据平台特点优化内容"])

def _get_authenticity_guidelines(element_type: str) -> List[str]:
    """获取文化真实性指导原则"""
    
    return [
        "尊重传统文化的原始含义",
        "避免文化符号的滥用和误用",
        "咨询当地文化专家的意见",
        "确保文化表达的准确性",
        "平衡传统保护与现代需求"
    ]

def _get_implementation_checklist(element_type: str) -> List[str]:
    """获取实施检查清单"""
    
    return [
        "文化专家审核",
        "当地社区反馈",
        "材料来源确认",
        "工艺质量检查",
        "维护保养计划"
    ]

def _get_booking_suggestions(activity_type: str) -> List[str]:
    """获取活动预订建议"""
    
    return [
        "提前24小时预约",
        "确认参与人数",
        "说明特殊需求",
        "准备相关物品",
        "了解活动注意事项"
    ]

def _get_follow_up_activities(activity_type: str) -> List[str]:
    """获取后续活动建议"""
    
    follow_up_map = {
        "茶文化体验": ["茶艺进阶班", "茶园参观", "茶具制作"],
        "纳西音乐分享会": ["乐器学习", "音乐创作", "文化讲座"],
        "东巴文化讲座": ["东巴文字学习", "传统手工艺", "文化深度游"]
    }
    
    return follow_up_map.get(activity_type, ["相关文化体验活动"])

def main():
    """主函数，启动 MCP 服务器"""
    try:
        # 验证配置
        Config.validate()
        logger.info("丽江客栈管理服务器启动中...")
        mcp.run()
    except Exception as e:
        logger.error(f"启动服务器时出错: {str(e)}")
        raise

if __name__ == "__main__":
    main()
