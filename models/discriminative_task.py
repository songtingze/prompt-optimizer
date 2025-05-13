from typing import Optional

from pydantic import BaseModel, Field


class OptimizeRequest(BaseModel):
    """
    判别式任务提示词优化接口的请求体
    """
    optimize_llm_config: dict  # 优化模型参数
    test_llm_config: dict  # 测试模型参数
    initial_prompt: str  # 初始提示词
    test_dataset: list  # 测试数据集和结果
    success_experience: Optional[str] = None  # 初始提示词的成功经验
    optimize_suggestion: Optional[str] = None  # 初始提示词的优化建议
    test_accuracy: Optional[float] = None  # 初始提示词的测试准确率


class OptimizeResponse(BaseModel):
    """
    判别式任务提示词优化接口的响应体
    """
    initial_prompt: str  # 初始提示词
    initial_success_experience: str  # 初始提示词的成功经验
    initial_optimize_suggestion: str  # 初始提示词的优化建议
    initial_test_accuracy: float  # 初始提示词的测试准确率
    optimized_prompt: str  # 优化后的提示词
    success_experience: str  # 优化后的提示词的成功经验
    optimize_suggestion: str  # 优化后的提示词的优化建议
    test_accuracy: float  # 优化后的提示词的测试准确率
    execution_time: str  # 优化过程中的执行时间
    total_tokens: int  # 优化过程中消耗的全部token数量
    test_result: list  # 测试数据集和结果


class ResponseWrapper(BaseModel):
    """统一响应包装器，封装API响应的标准格式"""
    code: str = Field(description="状态码")
    msg: str = Field(description="状态描述")
    data: Optional[OptimizeResponse] = Field(default=None, description="响应数据")
