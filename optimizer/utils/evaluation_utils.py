import re
from pathlib import Path
from typing import Any, List, Optional, Tuple, Dict
from optimizer.utils import load
import asyncio
import tiktoken
from concurrent.futures import ThreadPoolExecutor
import random
from optimizer.prompts.prompt_pool import EVALUATE_PROMPT

EVALUATION_REPETITION = 3
class EvaluationUtils:
    def __init__(self, root_path: Path) -> None:
        self.root_path = root_path

    def count_tokens(self, sample: dict):
        if not sample:
            return 0
        else:
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(str(sample["answers"])))

    def execute_prompt(self, optimizer: Any, current_prompt) -> dict:
        _, _, qa, _ = load.load_meta_data()
        answers = []

        # 同步版本的 fetch_answer 函数
        def fetch_answer(q: str) -> Dict[str, Any]:
            prompt = f"{current_prompt}\n\n{q}"
            try:
                answer, token_count = optimizer.execute_llm.generate_response(prompt)
                return {"question": q, "answer": answer}
            except Exception as e:
                return {"question": q, "answer": str(e)}

        # 提取所有问题
        questions = [item["question"] for item in qa]

        # 使用线程池并发执行 fetch_answer
        with ThreadPoolExecutor(max_workers=4) as executor:  # 可根据CPU核心数调整
            answers = list(executor.map(fetch_answer, questions))

        cur_round = optimizer.round
        new_data = {"round": cur_round, "answers": answers, "prompt": current_prompt}
        print("new_data:\n", new_data)
        return new_data

    def evaluate_prompt(
            self,
            optimizer: Any,
            samples: Optional[dict],
            new_samples: dict,
            path: Path,
            # data: List[dict],
            initial: bool = False,
    ) -> tuple[bool, Any, str | Any]:
        # evaluator = QuickEvaluate()
        new_token = self.count_tokens(new_samples)

        # 如果是第一轮没有最佳历史记录时
        if initial is True:
            samples = {"round": "0", "answers": "", "prompt": ""}
            _, modification_all = self._prompt_evaluate(optimizer, samples=samples, new_samples=new_samples)
            succeed = True
        else:
            evaluation_results = []
            modify_results = []

            def run_sync_evaluate() -> Tuple[bool, Any]:
                return self._prompt_evaluate(optimizer, samples=samples, new_samples=new_samples)

            # 使用线程池并发执行同步任务
            with ThreadPoolExecutor(max_workers=4) as executor:
                all_results = list(executor.map(
                    lambda _: run_sync_evaluate(),  # 使用 lambda 忽略参数
                    [None] * EVALUATION_REPETITION
                ))

            # 拆分所有结果为两个部分
            succeeds, modifications = zip(*all_results)

            # 合并到主列表中
            evaluation_results.extend(succeeds)
            modify_results.extend(modifications)

            # 输出调试信息
            print(f"Evaluation Results: {evaluation_results}")
            print(f"Modification Results: {modify_results}")

            # 计算最终的 succeed 值
            true_count = evaluation_results.count(True)
            false_count = evaluation_results.count(False)
            succeed = true_count > false_count

            # 只拼接与最终succeed值一致的modification
            filtered_modifications = [
                mod for s, mod in zip(evaluation_results, modify_results) if s == succeed
            ]
            modification_all = ' '.join(filtered_modifications)

        # 保存最佳prompt
        if(succeed):
            new_data = optimizer.data_utils.create_result_data(
                new_samples["round"], new_samples["answers"], new_samples["prompt"], succeed, new_token
            )
            result_path = optimizer.data_utils.get_best_results_file_path(path)
            optimizer.data_utils.save_best_results(result_path, new_data)

        answers = new_samples["answers"]

        return succeed, answers, modification_all

    def _prompt_evaluate(self, optimizer, samples, new_samples):
        _, requirement, qa, _ = load.load_meta_data()

        if random.random() < 0.5:
            samples, new_samples = new_samples, samples
            is_swapped = True
        else:
            is_swapped = False

        prompt = EVALUATE_PROMPT.format(
                    requirement=requirement, sample=samples, new_sample=new_samples, answers=str(qa))

        try:
            # response = await self.llm.responser(request_type=RequestType.EVALUATE, messages=messages)
            answer, _ = optimizer.evaluate_llm.generate_response(prompt)
            choose = extract_content(answer, "choose")
            analyse = extract_content(answer, "analyse")
            modification = extract_content(answer, "modification")
            return choose == "A" if is_swapped else choose == "B", modification

        except Exception as e:
            print(e)
            return False, "LLM分析反馈出现错误，请参考人工输入的修改反馈。"

def extract_content(xml_string: str, tag: str) -> Optional[str]:
    pattern = rf"<{tag}>(.*?)</{tag}>"
    match = re.search(pattern, xml_string, re.DOTALL)
    return match.group(1).strip() if match else None