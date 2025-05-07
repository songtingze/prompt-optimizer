import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict

from starlette.middleware.cors import CORSMiddleware

from examples.discriminative_task.optimizer_example import read_questions_and_units
from optimizer.core.prompt_optimizer import PromptOptimizer
from llm.llm_config import LLM_Config

app = FastAPI(
    title="Prompt Optimizer API",
    description="提示词优化API服务",
    version="1.0.0"
)

api_key = os.environ.get('API_KEY', '未找到PATH变量')

# 添加CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源，实际生产环境应该设置具体的源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)


class OptimizeRequest(BaseModel):
    initial_prompt: str  # 初始提示词
    success_experience: Optional[str] = None  # 初始提示词的成功经验
    optimize_suggestion: Optional[str] = None  # 初始提示词的优化建议
    test_accuracy: Optional[float] = None  # 初始提示词的测试准确率


class OptimizeResponse(BaseModel):
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


@app.post("/api/optimize", response_model=OptimizeResponse)
async def optimize_prompt(request: OptimizeRequest):
    try:
        # 优化和反思的大模型
        optimize_llm_config = LLM_Config(
            model_name="qwen-plus-latest",
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )

        # 测试数据集的大模型
        test_llm_config = LLM_Config(
            model_name="qwen2.5-32b-instruct",
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )

        # 创建优化器实例
        optimizer = PromptOptimizer(
            optimize_llm_config=optimize_llm_config,
            test_llm_config=test_llm_config
        )

        # 准备测试数据集（这里使用一个示例数据集，实际应用中可能需要根据具体场景调整）
        file_path = '../examples/discriminative_task/生成式搜索问题测评集-20250414.xlsx'
        sheet_name = '明细查询-薪资场景'

        test_dataset = []

        try:
            test_dataset = read_questions_and_units(file_path, sheet_name)
            print("读取结果：")
            for item in test_dataset:
                print(item)
        except Exception as e:
            print(f"读取文件时出错: {e}")

        # 定义评估函数
        def evaluation_func(response: str, test_case: dict) -> float:
            expected = str(test_case.get("expected", ""))
            if response == expected:
                return 1.0
            return 0.0

        # 运行优化
        result = optimizer.optimize(
            initial_prompt=request.initial_prompt,
            test_dataset=test_dataset,
            evaluation_func=evaluation_func,
            success_experience=request.success_experience,
            optimize_suggestion=request.optimize_suggestion
        )

        # 返回优化结果
        return OptimizeResponse(
            initial_prompt=request.initial_prompt,
            initial_success_experience=request.success_experience if request.success_experience else result[
                "initial_success_experience"],
            initial_optimize_suggestion=request.optimize_suggestion if request.optimize_suggestion else result[
                "initial_optimize_suggestion"],
            initial_test_accuracy=request.test_accuracy if request.test_accuracy else result["initial_accuracy"],
            optimized_prompt=result["optimize_prompt"],
            success_experience=result["success_experience"],
            optimize_suggestion=result["optimize_suggestion"],
            test_accuracy=result["accuracy"],
            execution_time=result["execution_time"],
            total_tokens=result["total_tokens"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
