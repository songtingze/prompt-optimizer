from typing import Dict, List, Optional, Tuple, Callable, Any
import json
from pathlib import Path
from llm.llm import LLM
from optimizer.prompts.system_prompts import REFLECTION_TEMPLATE1, OPTIMIZATION_TEMPLATE1
from llm.llm_config import LLM_Config
from datetime import datetime
from optimizer.utils import load
from optimizer.utils.prompt_utils import PromptUtils
from optimizer.utils.evaluation_utils import EvaluationUtils
from optimizer.utils.data_utils import DataUtils


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

    # 完整优化过程
    def optimize(self, current_prompt):
        # 2.执行优化后的prompt
        new_samples = self._execute_prompt()
        # 3.评估并反思
        self._evaluate_prompt(new_samples)
        # 1.优化（如果是第一轮则跳过该步骤）
        self._optimize_prompt(current_prompt)

        self.round += 1
        self.show_final_result()
        return self.round

    def _optimize_prompt(self, current_prompt):
        # prompt_path = self.root_path / "prompts"
        # load.set_file_name(self.template)

        if self.round == 1:
            # 第一次跳过优化
            self._handle_first_round_op(self.root_path)
        else:
            # 执行优化
            directory = self.prompt_utils.create_round_directory(self.root_path, self.round)
            new_prompt = self._generate_optimized_prompt()
            self.prompt = new_prompt
            print(f"\nRound {self.round} Prompt: {self.prompt}\n")
            # 记录该轮优化后的prompt
            self.prompt_utils.write_prompt(directory, prompt=self.prompt)
        return self.prompt

    def show_final_result(self):
        pass

    def _handle_first_round_op(self, prompt_path: Path, data: List[dict]) -> None:
        print("\n⚡ RUNNING Round 1 PROMPT ⚡\n")
        directory = self.prompt_utils.create_round_directory(prompt_path, self.round)

        # 读取初始化配置模板
        prompt, _, _, _ = load.load_meta_data()
        # 记录第一轮prompt
        self.prompt = prompt
        self.prompt_utils.write_prompt(directory, prompt=self.prompt)

        new_samples = await self.evaluation_utils.execute_prompt(self, directory)
        _, answers = await self.evaluation_utils.evaluate_prompt(
            self, None, new_samples, path=prompt_path, data=data, initial=True
        )
        self.prompt_utils.write_answers(directory, answers=answers)

    def _generate_optimized_prompt(self):
        pass

    def _execute_prompt(self):
        load.set_file_name(self.template)
        # 第一轮没有优化后的prompt
        if self.round == 1:
            # 读取初始化配置模板
            prompt, _, _, _ = load.load_meta_data()
            # 初始输入prompt
            self.prompt = prompt
            current_prompt = self.prompt
        else:
            # 读取上一轮优化后的prompt
            directory = self.prompt_utils.create_round_directory(self.root_path, self.round - 1)
            current_prompt = self.prompt_utils.load_prompt(self.round - 1, directory)
        print("\n⚡ RUNNING OPTIMIZED PROMPT ⚡\n")

        # 执行prompt
        new_samples = self.evaluation_utils.execute_prompt(self, current_prompt)
        return new_samples

    def _evaluate_prompt(self, new_samples):
        print("\n📊 EVALUATING OPTIMIZED PROMPT 📊\n")
        # 获取目前最好的结果
        samples = self.data_utils.get_best_round()
        # 用最新结果和最好结果进行比较评估
        success, answers = await self.evaluation_utils.evaluate_prompt(
            self, samples, new_samples, path=self.root_path, data=data, initial=(self.round == 1)
        )

        self.prompt_utils.write_answers(directory, answers=answers)
