import argparse
from typing import Tuple

from optimizer.core.prompt_optimizer_fewshot import PromptOptimizer
from llm.llm_config import LLM_Config
import yaml


def parse_args():
    parser = argparse.ArgumentParser(description="PromptOptimizer CLI")

    # LLM parameter
    parser.add_argument("--opt-model", type=str, default="deepseek-r1", help="Model for optimization")
    parser.add_argument("--opt-temp", type=float, default=0.7, help="Temperature for optimization")
    parser.add_argument("--eval-model", type=str, default="deepseek-r1", help="Model for evaluation")
    parser.add_argument("--eval-temp", type=float, default=0.3, help="Temperature for evaluation")
    parser.add_argument("--exec-model", type=str, default="deepseek-r1", help="Model for execution")
    parser.add_argument("--exec-temp", type=float, default=0.4, help="Temperature for execution")

    # PromptOptimizer parameter
    parser.add_argument("--workspace", type=str, default="../../results", help="Path for optimized output")
    parser.add_argument("--current_round", type=int, default=1, help="Initial round number")
    parser.add_argument("--max-rounds", type=int, default=10, help="Maximum number of rounds")
    parser.add_argument("--template", type=str, default="SummaryCJ.yaml", help="Template file name")
    parser.add_argument("--name", type=str, default="SummaryCJ", help="Project name")

    return parser.parse_args()


def load_config(config_path: str) -> dict:
    """从 YAML 文件加载配置"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def create_llm_config_from_yaml(
        config: dict,
        model_name: str,
        temperature: float
) -> LLM_Config:
    """
    根据 YAML 中的配置创建 LLM_Config 实例
    - 如果指定了 model_name，则从 models 字段中读取
    - 否则使用全局 llm 字段作为默认配置
    """

    if model_name in config.get("models", {}):
        model_config = config["models"][model_name]

    else:
        # 使用默认
        model_config = config["llm"]

    return LLM_Config(
        model_name=model_name,
        api_key=model_config["api_key"],
        base_url=model_config["base_url"],
        temperature=temperature
    )


# 启动第一轮优化
def start_optimization(optimizer) -> Tuple[str, str, int, str, bool]:

    rt_llm_feedback, rt_prompt, c_round, fn_answer, success = optimizer.optimize_first()

    return rt_llm_feedback, rt_prompt, c_round, fn_answer, success


# 继续优化
def continue_optimization(optimizer, current_round, user_feedback: str, llm_feedback:str, best_answer, best_prompt) -> Tuple[str, str, int, str, bool]:
    # 调用下一轮优化
    llm_feedback, current_prompt, next_round, fn_answer, success = optimizer.optimize_next(current_round, user_feedback, llm_feedback, best_answer, best_prompt)

    return llm_feedback, current_prompt, next_round, fn_answer, success

if __name__ == "__main__":
    args = parse_args()

    config = load_config("../../llm/config.yaml")

    # 构建 LLM 配置
    optimize_config = create_llm_config_from_yaml(config, args.opt_model, args.opt_temp)
    evaluate_config = create_llm_config_from_yaml(config, args.eval_model, args.eval_temp)
    execute_config = create_llm_config_from_yaml(config, args.exec_model, args.exec_temp)

    # 初始化优化、执行、评估反思三阶段优化器设置
    optimizer = PromptOptimizer(
        optimize_llm_config=optimize_config,
        evaluate_llm_config=evaluate_config,
        execute_llm_config=execute_config,
        rounds=args.current_round,
        optimized_path=args.workspace,
        template=args.template,
        name=args.name
    )

    # 启动第一轮优化
    llm_feedback, current_prompt, current_round, current_answer, success = start_optimization(optimizer)

    print(f"🚩 +++++++++返回前端接口结果+++round: {current_round-1}++++++ 🚩")
    print("返回的大模型优化反思：", llm_feedback)
    print("返回的当前优化后的prompt：", current_prompt)
    print("返回的当前优化后的问题执行结果：", current_answer)
    print("当前优化是否成功：", success)
    print("++++++++++++++++++++++++++++++++++++++")

    # 启动优化迭代
    while True:
        user_feedback = input("请用户根据上一轮的优化结果，输入你的优化建议（输入 'exit' 退出；没有建议则输入空字符串''）: ")
        if user_feedback.lower() == "exit":
            break

        llm_feedback, current_prompt, current_round, current_answer, success = continue_optimization(
            optimizer, current_round+1, user_feedback, llm_feedback, current_answer, current_prompt)

        print(f"🚩 +++++++++返回前端接口结果+++round: {current_round - 1}++++++ 🚩\n")
        print("返回的大模型优化反思：", llm_feedback, "\n")
        print("返回的当前优化后的prompt：", current_prompt, "\n")
        print("返回的当前优化后的问题执行结果：", current_answer, "\n")
        print("当前优化是否成功：", success)
        print("++++++++++++++++++++++++++++++++++++++")


