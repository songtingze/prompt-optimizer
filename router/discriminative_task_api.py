import os
from openai import OpenAI
from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from typing import Optional, List, Dict

from starlette.middleware.cors import CORSMiddleware

from examples.discriminative_task.optimizer_example import read_questions_and_units
from llm.llm import LLM
from models.discriminative_task import OptimizeResponse, OptimizeRequest
from optimizer.core.prompt_optimizer import PromptOptimizer
from llm.llm_config import LLM_Config

discriminative_task_router = APIRouter(prefix="/discriminative")


@discriminative_task_router.post("/api/optimize", response_model=OptimizeResponse)
async def optimize_prompt(request: OptimizeRequest):
    try:

        # 创建优化器实例
        optimizer = PromptOptimizer(
            optimize_llm_config=LLM_Config(model_name=request.optimize_llm_config["model_name"],
                                api_key=request.optimize_llm_config["api_key"],
                                base_url=request.optimize_llm_config["base_url"]),
            test_llm_config=LLM_Config(model_name=request.test_llm_config["model_name"],
                                api_key=request.test_llm_config["api_key"],
                                base_url=request.test_llm_config["base_url"])
        )

        # 定义评估函数
        def evaluation_func(response: str, test_case: dict) -> float:
            expected = str(test_case.get("expected", ""))
            if response == expected:
                return 1.0
            return 0.0

        # 运行优化
        result = optimizer.optimize(
            initial_prompt=request.initial_prompt,
            test_dataset=request.test_dataset,
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
            total_tokens=result["total_tokens"],
            test_result=request.test_dataset
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


