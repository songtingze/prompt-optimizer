from typing import Dict, List, Optional, Tuple, Callable, Any
import json
from llm.llm import LLM
from optimizer.prompts.system_prompts import REFLECTION_TEMPLATE1, OPTIMIZATION_TEMPLATE1
from llm.llm_config import LLM_Config
from datetime import datetime


class PromptOptimizer:
    def __init__(
            self,
            optimize_llm_config: LLM_Config,
            test_llm_config: LLM_Config,
    ):
        """
        初始化提示词优化器

        Args:
            model_name: 模型名称
            api_key: API密钥
            base_url: API基础URL
            **kwargs: 其他模型参数
        """
        self.optimize_llm = LLM(
            model_name=optimize_llm_config.model_name,
            api_key=optimize_llm_config.api_key,
            base_url=optimize_llm_config.base_url
        )
        self.test_llm = LLM(
            model_name=test_llm_config.model_name,
            api_key=test_llm_config.api_key,
            base_url=test_llm_config.base_url
        )

    # 优化提示词
    def optimize_prompt(
            self,
            prompt: str,
            optimize_suggestion: str,
    ) -> Tuple[str, int]:
        # 生成优化后的提示词
        optimization_prompt = OPTIMIZATION_TEMPLATE1.format(
            original_prompt=prompt,
            optimize_suggestion=optimize_suggestion,
        )

        optimized_prompt, tokens = self.optimize_llm.generate_response(optimization_prompt)
        print(f"优化的提示词：\n{optimized_prompt}")
        return optimized_prompt, tokens

    # 评估+反思提示词
    def evaluate_reflect_prompt(
            self,
            prompt: str,
            test_dataset: List[Dict],
            evaluation_func: Callable[[str, Dict], float]
    ) -> tuple[list[dict[str, float | None | Any]], float | int, Any, int]:
        # 评估当前提示词
        """评估提示词在测试数据集上的效果"""
        test_results = []
        test_positive_results = []
        test_nagative_results = []
        total_tokens = 0

        for test_case in test_dataset:
            # 使用提示词生成回复
            response, tokens = self.test_llm.generate_response_with_system_prompt(prompt, str(test_case["input"]))
            total_tokens += tokens
            # 使用评估函数计算分数
            score = evaluation_func(response, test_case)

            if score > 0.7:
                test_positive_results.append({
                    "input": test_case["input"],
                    "output": response,
                    "expected": test_case.get("expected", None),
                    "score": score
                })
            else:
                test_nagative_results.append({
                    "input": test_case["input"],
                    "output": response,
                    "expected": test_case.get("expected", None),
                    "score": score
                })

            print(f"用户问题：{test_case}")
            print(f"生成结果：{response}")
            print(f"分数：{score}")

            test_results.append({
                "input": test_case["input"],
                "output": response,
                "expected": test_case.get("expected", None),
                "score": score
            })
        accuracy = len(test_positive_results) / len(test_results) if test_results else 0
        print(f"测试准确率：{len(test_positive_results)}/{len(test_results)} = {accuracy}")

        """反思并提出改进建议"""
        # 生成反思提示词
        reflection_prompt = REFLECTION_TEMPLATE1.format(
            original_prompt=prompt,
            test_positive_results=json.dumps(test_positive_results, ensure_ascii=False, indent=2),
            test_nagative_results=json.dumps(test_nagative_results, ensure_ascii=False, indent=2),
            accuracy=accuracy
        )

        optimize_suggestion, tokens = self.optimize_llm.generate_response(reflection_prompt)
        total_tokens += tokens
        print(f"优化建议：\n{optimize_suggestion}")
        return test_nagative_results, accuracy, optimize_suggestion, total_tokens

    # 完整优化过程
    def optimize(
            self,
            initial_prompt: str,
            test_dataset: List[Dict],
            evaluation_func: Callable[[str, Dict], float],
            optimize_suggestion: Optional[str]
    ) -> Dict:
        """核心优化迭代"""

        current_prompt = initial_prompt
        # best_score = float('-inf')
        # best_prompt = initial_prompt
        history = []
        total_tokens = 0
        start_time_total = datetime.now()

        if optimize_suggestion is None:
            print("-----------------------开始评估初始提示词--------------------------")
            start_time_initial_evaluate = datetime.now()
            # 评估当前提示词
            test_nagative_results, accuracy, optimize_suggestion, tokens = self.evaluate_reflect_prompt(
                current_prompt, test_dataset, evaluation_func
            )
            total_tokens += tokens

            end_time_initial_evaluate = datetime.now()
            execution_time = end_time_initial_evaluate - start_time_initial_evaluate
            # 记录历史
            history.append({
                "step": "evaluate_initial_prompt",
                "prompt": current_prompt,
                "test_nagative_results": test_nagative_results,
                "optimize_suggestion": optimize_suggestion,
                "accuracy": accuracy,
                "tokens": tokens,
                "execution_time": str(execution_time.total_seconds())
            })

            print(
                f"-----------------------初始提示词评估结束,时长{end_time_initial_evaluate - start_time_initial_evaluate}--------------------------")

        print("-----------------------开始优化提示词--------------------------")
        start_time_optimize = datetime.now()
        # 根据优化建议优化提示词
        optimize_prompt, tokens = self.optimize_prompt(current_prompt, optimize_suggestion)
        total_tokens += tokens
        current_prompt = optimize_prompt

        end_time_optimize = datetime.now()
        execution_time = end_time_optimize - start_time_optimize
        # 记录历史
        history.append({
            "step": "optimize_prompt",
            "optimize_prompt": optimize_prompt,
            "tokens": tokens,
            "execution_time": str(execution_time.total_seconds())
        })
        print(f"-----------------------提示词优化结束,时长{end_time_optimize - start_time_optimize}--------------------------")
        print("-----------------------开始评估优化提示词--------------------------")

        start_time_evaluate = datetime.now()
        # 评估当前提示词
        test_nagative_results, accuracy, optimize_suggestion, tokens = self.evaluate_reflect_prompt(
            current_prompt, test_dataset, evaluation_func
        )
        total_tokens += tokens

        end_time_evaluate = datetime.now()
        execution_time = end_time_evaluate - start_time_evaluate
        # 记录历史
        history.append({
            "step": "evaluate_prompt",
            "prompt": current_prompt,
            "test_nagative_results": test_nagative_results,
            "optimize_suggestion": optimize_suggestion,
            "accuracy": accuracy,
            "tokens": tokens,
            "execution_time": str(execution_time.total_seconds())
        })

        print(f"-----------------------优化提示词评估结束,时长{end_time_evaluate - start_time_evaluate}--------------------------")

        end_time_total = datetime.now()
        execution_time = end_time_total - start_time_total
        history.append({
            "step": "optimize_finish",
            "prompt": current_prompt,
            "optimize_suggestion": optimize_suggestion,
            "accuracy": accuracy,
            "tokens": total_tokens,
            "execution_time": str(execution_time.total_seconds())
        })
        print(f"-----------------------优化结束,时长{end_time_total - start_time_total}--------------------------")
        execution_time = end_time_total - start_time_total
        return {
            "optimize_prompt": optimize_prompt,
            "history": history,
            "total_tokens": total_tokens,
            "execution_time": str(execution_time.total_seconds())
        }
