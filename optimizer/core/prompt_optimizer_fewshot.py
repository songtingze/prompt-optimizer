import asyncio
from typing import Dict, List, Optional, Tuple, Callable, Any
import json
from pathlib import Path
from llm.llm import LLM
from optimizer.prompts.system_prompts import REFLECTION_TEMPLATE1, OPTIMIZATION_TEMPLATE1
from llm.llm_config import LLM_Config
from datetime import datetime
from optimizer.utils import load
from optimizer.utils.prompt_utils import PromptUtils
from optimizer.utils.evaluation_utils import EvaluationUtils, extract_content
from optimizer.utils.data_utils import DataUtils
from optimizer.prompts.prompt_pool import PROMPT_OPTIMIZE_PROMPT


class PromptOptimizer:
    def __init__(
            self,
            optimize_llm_config: LLM_Config,
            evaluate_llm_config: LLM_Config,
            execute_llm_config: LLM_Config,
            rounds: int,
            optimized_path: str = None,
            name: str = "",
            template: str = ""
    ):
        """
        初始化提示词优化器

        Args:
            model_name: 模型名称
            api_key: API密钥
            base_url: API基础URL
            temperature: 模型temperature
            **kwargs: 其他模型参数
        """
        self.optimize_llm = LLM(
            model_name=optimize_llm_config.model_name,
            api_key=optimize_llm_config.api_key,
            base_url=optimize_llm_config.base_url,
            temperature=optimize_llm_config.temperature
        )

        self.evaluate_llm = LLM(
            model_name=evaluate_llm_config.model_name,
            api_key=evaluate_llm_config.api_key,
            base_url=evaluate_llm_config.base_url,
            temperature=evaluate_llm_config.temperature
        )

        self.execute_llm = LLM(
            model_name=execute_llm_config.model_name,
            api_key=execute_llm_config.api_key,
            base_url=execute_llm_config.base_url,
            temperature=execute_llm_config.temperature
        )

        self.name = name
        self.root_path = Path(optimized_path) / self.name
        self.top_scores = []
        self.round = rounds
        # self.max_rounds = max_rounds
        self.template = template
        self.prompt_utils = PromptUtils(self.root_path)
        self.evaluation_utils = EvaluationUtils(self.root_path)
        self.data_utils = DataUtils(self.root_path)
        # self.evaluation_utils = EvaluationUtils(self.root_path)


    # 第一轮优化过程
    def optimize_first(self):
        # 2.执行优化后的prompt
        new_samples = self._execute_prompt(initial=True)
        # 3.评估并反思
        llm_feedback, _ = self._evaluate_prompt(new_samples, None, initial=True)
            # self._run_async_evaluate(new_samples, initial=True)
        self.round += 1
        best_samples = self.data_utils.get_best_round()
        # 1.优化更新prompt
        self._optimize_prompt_first(llm_feedback, best_samples["answers"], best_samples["prompt"])
        # 2.执行优化后的prompt
        new_samples = self._execute_prompt()
        # 3.评估并反思
        llm_feedback, success = self._evaluate_prompt(new_samples, best_samples)
        # 结果展示并返回
        best_round = self.data_utils.get_best_round()
        self.show_final_result(success, best_round)
        return llm_feedback, self.prompt, self.round, best_round['answers'], success

    # 循环优化过程
    def optimize_next(self, current_round, user_feedback: str, llm_feedback: str, best_answer, best_prompt):
        self.round = current_round
        # 1.优化更新prompt(使用两个来源反馈+之前的最佳prompt和对应得到的示例答案)
        self._optimize_prompt_next(llm_feedback, user_feedback, best_answer, best_prompt)
        # 2.执行优化后的prompt
        new_samples = self._execute_prompt()
        # 3.评估并反思
        best_samples = {
            "prompt": best_prompt,
            "answers": best_answer
        }
        llm_feedback, success = self._evaluate_prompt(new_samples, best_samples)
        # 目前最优结果
        best_round = self.data_utils.get_best_round()
        self.show_final_result(success, best_round)
        return llm_feedback, self.prompt, self.round, best_round['answers'], success

    def _optimize_prompt_first(self, llm_feedback, answer, best_prompt):
        new_prompt = self._generate_optimized_prompt(llm_feedback, "", answer, best_prompt)
        self.prompt = new_prompt
        print(f"\n Prompt: {self.prompt}\n")

        # 保存优化后prompt
        directory = self.prompt_utils.create_round_directory(self.root_path, self.round)
        self.prompt_utils.write_prompt(directory, prompt=self.prompt)

    def show_final_result(self, success, best_round):
        # best_round = self.data_utils.get_best_round()

        print("\n" + "=" * 50)
        print("\n🏆 OPTIMIZATION COMPLETED - FINAL RESULTS 🏆\n")
        print(f"\n Optimization: {'✅ SUCCESS' if success else '❌ FAILED'}\n")
        print(f"\n✨ Final Optimized Prompt:\n{best_round['prompt']}")
        print(f"\n🎯 According Answer:\n{best_round['answers']}")
        print("\n" + "=" * 50 + "\n")

    def _optimize_prompt_next(self, llm_feedback, human_feedback, answer, best_prompt):
        new_prompt = self._generate_optimized_prompt(llm_feedback, human_feedback, answer, best_prompt)
        self.prompt = new_prompt

        # 保存优化后prompt
        directory = self.prompt_utils.create_round_directory(self.root_path, self.round)
        self.prompt_utils.write_prompt(directory, prompt=self.prompt)

    def _generate_optimized_prompt(self, llm_feedback, human_feedback, answer, best_prompt):
        _, requirements, qa, count = load.load_meta_data()

        print(f"\n🚀OPTIMIZATION STARTING 🚀\n")
        print(f"\nSelecting prompt and advancing to the iteration phase\n")

        golden_answer = self.data_utils.list_to_markdown(qa)
        best_answer = self.data_utils.list_to_markdown(answer)

        # 第一轮优化不补充用户反馈
        if human_feedback == "":
            print(f"LLM Modification: {llm_feedback}")

            optimize_prompt = PROMPT_OPTIMIZE_PROMPT.format(
                prompt=best_prompt,
                answers=best_answer,
                requirements=requirements,
                golden_answers=golden_answer,
                count=count,
                LLM_feedback=llm_feedback,
                human_feedback=human_feedback
            )
        else:
            print(f"LLM Modification: {llm_feedback}\n")
            print(f"Human Modification: {human_feedback}")

            optimize_prompt = PROMPT_OPTIMIZE_PROMPT.format(
                prompt=best_prompt,
                answers=best_answer,
                requirements=requirements,
                golden_answers=golden_answer,
                count=count,
                LLM_feedback=llm_feedback,
                human_feedback=human_feedback
            )

        response, _ = self.optimize_llm.generate_response(optimize_prompt)
        prompt = extract_content(response, "prompt")

        return prompt if prompt else ""

    def _execute_prompt(self, initial=False):
        load.set_file_name(self.template)
        # 第一轮没有优化后的prompt
        if initial:
            # 读取初始化配置模板
            prompt, _, _, _ = load.load_meta_data()
            # 初始输入prompt
            self.prompt = prompt
            current_prompt = self.prompt
        else:
            # 读取上一轮优化后的prompt
            # directory = self.prompt_utils.create_round_directory(self.root_path, self.round)
            # current_prompt = self.prompt_utils.load_prompt(self.round, directory)
            current_prompt = self.prompt
        print("\n⚡ RUNNING OPTIMIZED PROMPT ⚡\n")
        print(f"\n Current_prompt:{current_prompt}\n")

        # 执行prompt
        # new_samples = self._run_async_execute(current_prompt)
        new_samples = self.evaluation_utils.execute_prompt(self, current_prompt)
        return new_samples

    def _evaluate_prompt(self, new_samples, best_samples, initial=False):
        print("\n📊 EVALUATING OPTIMIZED PROMPT 📊\n")
        # 获取目前最好的结果
        # best_samples = self.data_utils.get_best_round()
        # 用最新结果和最好结果进行比较评估
        success, answers, modification_all = self.evaluation_utils.evaluate_prompt(
            self, best_samples, new_samples, path=self.root_path, initial=initial
        )
        # 保存评估结果（有可能success为false，保存的并不一定为最佳）
        directory = self.prompt_utils.create_round_directory(self.root_path, self.round)
        self.prompt_utils.write_answers(directory, success, modification_all, answers=answers)

        return modification_all, success

