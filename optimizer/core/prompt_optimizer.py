from typing import Dict, List, Optional, Tuple, Callable, Any
import json

from llm.Message import system_message, user_message
from llm.llm import LLM
from optimizer.prompts.system_prompts import OPTIMIZATION_SYSTEM_PROMPT, \
    OPTIMIZATION_USER_PROMPT, REFLECTION_SYSTEM_PROMPT, REFLECTION_USER_PROMPT
from llm.llm_config import LLM_Config
from datetime import datetime
from optimizer.prompts.prompt_template import BROKE_TEMPLATE


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
            success_experience: str,
            optimize_suggestion: str,
            test_dataset: List[Dict],
    ) -> Tuple[str, int]:
        # 生成优化后的提示词
        optimization_prompt = OPTIMIZATION_USER_PROMPT.format(
            original_prompt=prompt,
            success_experience=success_experience,
            optimize_suggestion=optimize_suggestion,
            prompt_template=BROKE_TEMPLATE,
            test_dataset=test_dataset,
        )

        messages = [system_message(OPTIMIZATION_SYSTEM_PROMPT), user_message(optimization_prompt)]
        optimized_result, tokens = self.optimize_llm.generate_response_stream(messages)
        optimized_prompt = self.extract_new_prompt(optimized_result)
        # print(f"优化结果：\n{optimized_result}")
        return optimized_prompt, tokens

    def extract_new_prompt(self, text: str) -> str:
        """
        提取优化结果中的新提示词
        """
        # 提取新提示词部分并保留原始格式
        new_prompt = text.split("<新提示词>")[1].split("</新提示词>")[0].strip()
        return new_prompt

    # 评估+反思提示词
    def evaluate_reflect_prompt(
            self,
            prompt: str,
            test_dataset: List[Dict],
            evaluation_func: Callable[[str, Dict], float]
    ) -> tuple[list[dict[str, str | float | None | Any]], float | int, str, str, int]:
        # 评估当前提示词
        """评估提示词在测试数据集上的效果"""
        test_results = []
        test_positive_results = []
        test_negative_results = []
        total_tokens = 0

        for test_case in test_dataset:
            # 使用提示词生成回复
            messages = [system_message(prompt), user_message(str(test_case["input"]))]
            response, tokens = self.test_llm.generate_response(messages)
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
                test_negative_results.append({
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
        reflection_prompt = REFLECTION_USER_PROMPT.format(
            original_prompt=prompt,
            test_positive_results=json.dumps(test_positive_results, ensure_ascii=False, indent=2),
            test_negative_results=json.dumps(test_negative_results, ensure_ascii=False, indent=2),
            accuracy=accuracy,
            threshold=0.9
        )

        messages = [system_message(REFLECTION_SYSTEM_PROMPT), user_message(reflection_prompt)]
        reflect_result, tokens = self.optimize_llm.generate_response_stream(messages)
        total_tokens += tokens
        result = self.extract_success_experience_and_optimize_suggestion(reflect_result)

        # print(f"反思结果：\n{reflect_result}")
        return test_negative_results, accuracy, result["success_experience"], result[
            "optimize_suggestion"], total_tokens

    def extract_success_experience_and_optimize_suggestion(self, text: str) \
            -> Dict:
        """
        提取反思结果中的成功经验和优化建议
        """
        # 提取成功经验部分并保留原始格式
        success_block = text.split("<成功经验>")[1].split("</成功经验>")[0].strip()
        # 提取优化建议部分并保留原始格式
        suggestion_block = text.split("<优化建议>")[1].split("</优化建议>")[0].strip()

        return {
            "success_experience": success_block,
            "optimize_suggestion": suggestion_block
        }

    # 完整优化过程
    def optimize(
            self,
            initial_prompt: str,
            test_dataset: List[Dict],
            evaluation_func: Callable[[str, Dict], float],
            success_experience: Optional[str],
            optimize_suggestion: Optional[str]
    ) -> Dict:
        """核心优化迭代"""

        current_prompt = initial_prompt
        # best_score = float('-inf')
        # best_prompt = initial_prompt
        history = []
        total_tokens = 0
        start_time_total = datetime.now()

        # 记录初始提示词的评估信息
        initial_accuracy = -1.0
        initial_success_experience = ""
        initial_optimize_suggestion = ""

        if optimize_suggestion is None:
            print("-----------------------开始评估初始提示词--------------------------")
            start_time_initial_evaluate = datetime.now()
            # 评估当前提示词
            test_nagative_results, accuracy, success_experience, optimize_suggestion, tokens = self.evaluate_reflect_prompt(
                current_prompt, test_dataset, evaluation_func
            )
            total_tokens += tokens

            end_time_initial_evaluate = datetime.now()
            execution_time = end_time_initial_evaluate - start_time_initial_evaluate

            # 记录初始提示词的评估信息
            initial_accuracy = accuracy
            initial_success_experience = success_experience
            initial_optimize_suggestion= optimize_suggestion

            # 记录历史
            history.append({
                "step": "evaluate_initial_prompt",
                "prompt": current_prompt,
                "test_nagative_results": test_nagative_results,
                "success_experience": success_experience,
                "optimize_suggestion": optimize_suggestion,
                "accuracy": accuracy,
                "tokens": tokens,
                "execution_time": str(execution_time.total_seconds())
            })

            print(f"-----------------------初始提示词评估结束,时长{end_time_initial_evaluate - start_time_initial_evaluate}--------------------------")

        print("-----------------------开始优化提示词--------------------------")
        start_time_optimize = datetime.now()
        # 根据优化建议优化提示词
        optimize_prompt, tokens = self.optimize_prompt(current_prompt, success_experience, optimize_suggestion, test_dataset)
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
        test_nagative_results, accuracy, success_experience, optimize_suggestion, tokens = self.evaluate_reflect_prompt(
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
            "success_experience":success_experience,
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
            "execution_time": str(execution_time.total_seconds()),
            "accuracy": accuracy,
            "initial_accuracy": initial_accuracy,
            "success_experience": success_experience,
            "optimize_suggestion": optimize_suggestion,
            "initial_success_experience":initial_success_experience,
            "initial_optimize_suggestion":initial_optimize_suggestion
        }
