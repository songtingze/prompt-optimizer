from llm.llm_t import LLM
from llm.llm_config import LLM_Config
from optimizer.utils.evaluation_utils import extract_content, list_to_markdown, EvaluationUtils
from optimizer.prompts.prompt_pool import PROMPT_OPTIMIZE_PROMPT
from utils.logger import logger

# from optimizer.prompts.prompt_template import BROKE_TEMPLATE

class PromptOptimizer:
    def __init__(
            self,
            optimize_llm_config: LLM_Config,
            evaluate_llm_config: LLM_Config,
            execute_llm_config: LLM_Config,
            # rounds: int,
            # optimized_path: str = None,
            # name: str = "",
            # template: str = ""
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

        # self.name = name
        # self.root_path = Path(optimized_path) / self.name
        self.top_scores = []
        # self.round = rounds
        # self.max_rounds = max_rounds
        # self.template = template
        # self.prompt_utils = PromptUtils(self.root_path)
        self.evaluation_utils = EvaluationUtils()
        # self.data_utils = DataUtils(self.root_path)
        # self.evaluation_utils = EvaluationUtils(self.root_path)

    # 第一轮优化过程 todo:初始接收问答对
    def optimize_first(self, current_prompt, qa_list):
        # 2.执行优化后的prompt
        new_samples = self._execute_prompt(current_prompt, qa_list)
        # 3.评估并反思
        modification_all, anaysis_all, _ = self._evaluate_prompt(new_samples, None, qa_list, initial=True)
        # self._run_async_evaluate(new_samples, initial=True)
        # self.round += 1
        # best_samples = self.data_utils.get_best_round()
        # 1.优化更新prompt(基于上一轮的prompt)
        new_prompt = self._optimize_prompt(modification_all, anaysis_all, new_samples["answers"], new_samples["prompt"],
                                           qa_list)
        # 2.执行优化后的prompt
        last_samples = new_samples
        new_samples = self._execute_prompt(new_prompt, qa_list)
        # 3.评估并反思
        modification_all, anaysis_all, success = self._evaluate_prompt(new_samples, last_samples, qa_list)
        # 结果展示并返回最新
        # best_round = self.data_utils.get_best_round()
        self.show_final_result(success, new_samples)
        return modification_all, anaysis_all, new_prompt, new_samples['answers'], success

    # 循环优化过程 todo:初始接收问答对
    def optimize_next(self, modification_all: str, anaysis_all: str, last_answer, last_prompt, qa_list):
        # self.round = current_round
        # 1.优化更新prompt(使用两个来源反馈+之前的最佳prompt和对应得到的示例答案)
        new_prompt = self._optimize_prompt(modification_all, anaysis_all, last_answer, last_prompt, qa_list)
        # 2.执行优化后的prompt
        new_samples = self._execute_prompt(new_prompt, qa_list)
        # 3.评估并反思
        last_sample = {
            "prompt": last_prompt,
            "answers": last_answer
        }
        modification_all, anaysis_all, success = self._evaluate_prompt(new_samples, last_sample, qa_list)
        # 目前最新结果
        # best_round = self.data_utils.get_best_round()
        self.show_final_result(success, new_samples)
        return modification_all, anaysis_all, new_prompt, new_samples['answers'], success

    def _optimize_prompt(self, modification_all, anaysis_all, answer, current_prompt, qa_list):
        new_prompt = self._generate_optimized_prompt(modification_all, anaysis_all, answer, current_prompt, qa_list)
        self.prompt = new_prompt
        logger.info(f"\n New Prompt: {new_prompt}\n")
        return new_prompt

        # # 保存优化后prompt
        # directory = self.prompt_utils.create_round_directory(self.root_path, self.round)
        # self.prompt_utils.write_prompt(directory, prompt=self.prompt)

    def show_final_result(self, success, new_samples):
        # best_round = self.data_utils.get_best_round()

        logger.info("\n" + "=" * 50)
        logger.info("\n🏆 OPTIMIZATION COMPLETED - FINAL RESULTS 🏆\n")
        logger.info(f"\n Optimization: {'✅ SUCCESS' if success else '❌ FAILED'}\n")
        logger.info(f"\n✨ Final Optimized Prompt:\n{new_samples['prompt']}")
        logger.info(f"\n🎯 According Answer:\n{new_samples['answers']}")
        logger.info("\n" + "=" * 50 + "\n")

    # def _optimize_prompt_next(self, llm_feedback, human_feedback, answer, best_prompt):
    #     new_prompt = self._generate_optimized_prompt(modification_all, anaysis_all, answer, best_prompt)
    #     self.prompt = new_prompt
    #
    #     # 保存优化后prompt
    #     directory = self.prompt_utils.create_round_directory(self.root_path, self.round)
    #     self.prompt_utils.write_prompt(directory, prompt=self.prompt)

    def _generate_optimized_prompt(self, modification_all, anaysis_all, answer, current_prompt, qa):
        # _, requirements, qa, count = load.load_meta_data()

        logger.info(f"\n🚀OPTIMIZATION STARTING 🚀\n")
        logger.info(f"\nSelecting prompt and advancing to the iteration phase\n")

        golden_answer = list_to_markdown(qa)
        best_answer = list_to_markdown(answer)

        # 第一轮优化不补充用户反馈
        logger.info(f"Feedback: {anaysis_all}\n\n{modification_all}")

        # optimize_prompt = PROMPT_OPTIMIZE_PROMPT.format(
        #     prompt=current_prompt,
        #     answers=best_answer,
        #     requirements=requirements,
        #     golden_answers=golden_answer,
        #     count=count,
        #     anaysis_all=anaysis_all,
        #     modification_all=modification_all
        #     # template=BROKE_TEMPLATE
        # )
        optimize_prompt = PROMPT_OPTIMIZE_PROMPT.format(
            prompt=current_prompt,
            answers=best_answer,
            golden_answers=golden_answer,
            anaysis_all=anaysis_all,
            modification_all=modification_all,
            count=""
            # template=BROKE_TEMPLATE
        )

        response, _ = self.optimize_llm.generate_response(optimize_prompt)
        new_prompt = extract_content(response, "prompt")

        return new_prompt if new_prompt else ""

    def _execute_prompt(self, current_prompt, qa_list):
        # load.set_file_name(self.template)
        # # 第一轮没有优化后的prompt
        # if initial:
        #     # 读取初始化配置模板
        #     prompt, _, _, _ = load.load_meta_data()
        #     # 初始输入prompt
        #     self.prompt = prompt
        #     current_prompt = self.prompt
        # else:
        #     # 读取上一轮优化后的prompt
        #     # directory = self.prompt_utils.create_round_directory(self.root_path, self.round)
        #     # current_prompt = self.prompt_utils.load_prompt(self.round, directory)
        #     current_prompt = self.prompt
        logger.info("\n⚡ RUNNING OPTIMIZED PROMPT ⚡\n")
        logger.info(f"\n Current_prompt:{current_prompt}\n")

        # 执行prompt
        # new_samples = self._run_async_execute(current_prompt)
        new_samples = self.evaluation_utils.execute_prompt(self, current_prompt, qa_list)
        return new_samples

    def _evaluate_prompt(self, new_samples, last_samples, qa_list, initial=False):
        logger.info("\n📊 EVALUATING OPTIMIZED PROMPT 📊\n")
        # 获取目前最好的结果
        # best_samples = self.data_utils.get_best_round()
        # 用最新结果和上一次结果进行比较评估
        success, modification_all, anaysis_all = self.evaluation_utils.evaluate_prompt(
            self, last_samples, new_samples, qa_list, initial=initial
        )
        # 保存评估结果（有可能success为false，保存的并不一定为最佳）
        # directory = self.prompt_utils.create_round_directory(self.root_path, self.round)
        # self.prompt_utils.write_answers(directory, success, modification_all, answers=answers)

        return modification_all, anaysis_all, success
