from typing import Optional

from pydantic import BaseModel, Field

class OptimizeRequest(BaseModel):
    """
    生成式任务提示词优化接口的请求体
    """
    optimize_llm_config: dict  # 优化评估模型参数
    exe_llm_config: dict  # 执行模型参数
    current_prompt: str  # 当前的提示词
    current_answer: Optional[list] = None  # 当前的提示词对应的答案（QA对）
    qa_list: list  # 用户输入的示例用于评估优化（QA对）
    anaysis: Optional[str] = None  # 当前提示词的缺点分析
    modifications: Optional[str] = None  # 当前提示词的优化建议


class OptimizeResponse(BaseModel):
    """
    生成式任务提示词优化接口的响应体
    """
    initial_prompt: str  # 初始提示词
    initial_anaysis: Optional[str]  # 初始提示词的缺点分析
    initial_modifications: Optional[str]  # 初始提示词的优化建议
    initial_answer: Optional[list]  # 初始提示词的答案（QA对）
    new_prompt: str  # 优化后的提示词
    new_answer: list  # 优化后的提示词的答案（QA对）
    anaysis: str  # 优化后的提示词的缺点分析
    modifications: str  # 优化后的提示词的优化建议
    success: bool  # 本次优化大模型评估


class ResponseWrapper(BaseModel):
    """统一响应包装器，封装API响应的标准格式"""
    code: str = Field(description="状态码")
    msg: str = Field(description="状态描述")
    data: Optional[OptimizeResponse] = Field(default=None, description="响应数据")