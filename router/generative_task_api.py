from fastapi import FastAPI, HTTPException, APIRouter

from llm.llm_config import LLM_Config
from optimizer.core.prompt_optimizer_fewshot import PromptOptimizer

from models.generative_task import OptimizeResponse, OptimizeRequest

generative_task_router = APIRouter(prefix="/generative")


# optimizer = None

@generative_task_router.post("/api/optimizeFirst", response_model=OptimizeResponse)
async def start_optimization(request: OptimizeRequest):
    try:
        # 初始化优化、执行、评估反思三阶段优化器设置
        optimizer = PromptOptimizer(
            optimize_llm_config=LLM_Config(
                model_name=request.optimize_llm_config["model_name"],
                api_key=request.optimize_llm_config["api_key"],
                base_url=request.optimize_llm_config["base_url"],
                temperature=request.optimize_llm_config["temperature"]
            ),
            evaluate_llm_config=LLM_Config(
                model_name=request.optimize_llm_config["model_name"],
                api_key=request.optimize_llm_config["api_key"],
                base_url=request.optimize_llm_config["base_url"],
                temperature=request.optimize_llm_config["temperature"]
            ),
            execute_llm_config=LLM_Config(
                model_name=request.exe_llm_config["model_name"],
                api_key=request.exe_llm_config["api_key"],
                base_url=request.exe_llm_config["base_url"],
                temperature=request.exe_llm_config["temperature"]
            )
        )

        # 启动第一轮优化
        modification_all, anaysis_all, new_prompt, new_answer, success = optimizer.optimize_first(
            request.current_prompt, request.qa_list)

        # 返回优化结果
        return OptimizeResponse(
            initial_prompt=request.current_prompt,  # 初始提示词
            initial_anaysis=request.anaysis,  # 初始提示词的缺点分析
            initial_modifications=request.modifications,  # 初始提示词的优化建议
            initial_answer=request.current_answer,  # 初始提示词的答案（QA对）
            new_prompt=new_prompt,  # 优化后的提示词
            new_answer=new_answer,  # 优化后的提示词的答案（QA对）
            anaysis=anaysis_all,  # 优化后的提示词的缺点分析
            modifications=modification_all,  # 优化后的提示词的优化建议
            success=success  # 本次优化大模型评估
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@generative_task_router.post("/api/optimizeNext", response_model=OptimizeResponse)
async def continue_optimization(request: OptimizeRequest):
    try:
        # 初始化优化、执行、评估反思三阶段优化器设置
        optimizer = PromptOptimizer(
            optimize_llm_config=LLM_Config(
                model_name=request.optimize_llm_config["model_name"],
                api_key=request.optimize_llm_config["api_key"],
                base_url=request.optimize_llm_config["base_url"],
                temperature=request.optimize_llm_config["temperature"]
            ),
            evaluate_llm_config=LLM_Config(
                model_name=request.optimize_llm_config["model_name"],
                api_key=request.optimize_llm_config["api_key"],
                base_url=request.optimize_llm_config["base_url"],
                temperature=request.optimize_llm_config["temperature"]
            ),
            execute_llm_config=LLM_Config(
                model_name=request.exe_llm_config["model_name"],
                api_key=request.exe_llm_config["api_key"],
                base_url=request.exe_llm_config["base_url"],
                temperature=request.exe_llm_config["temperature"]
            )
        )

        # 启动迭代优化
        modification_all, anaysis_all, new_prompt, new_answer, success = optimizer.optimize_next(
            request.modifications, request.anaysis, request.current_answer, request.current_prompt, request.qa_list)

        # 返回优化结果
        return OptimizeResponse(
            initial_prompt=request.current_prompt,  # 初始提示词
            initial_anaysis=request.anaysis,  # 初始提示词的缺点分析
            initial_modifications=request.modifications,  # 初始提示词的优化建议
            initial_answer=request.current_answer,  # 初始提示词的答案（QA对）
            new_prompt=new_prompt,  # 优化后的提示词
            new_answer=new_answer,  # 优化后的提示词的答案（QA对）
            anaysis=anaysis_all,  # 优化后的提示词的缺点分析
            modifications=modification_all,  # 优化后的提示词的优化建议
            success=success  # 本次优化大模型评估
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
