from datetime import datetime

from optimizer.core.prompt_optimizer import PromptOptimizer
from typing import Dict
import json
import pandas as pd
from llm.llm_config import LLM_Config
from examples.discriminative_task.prompts.test_prompts import test_prompt


def example_evaluation_func(response: str, test_case: Dict) -> float:
    """
    示例评估函数 - 可以根据具体任务自定义评估标准
    这里使用一个简单的评分方案：检查响应中是否包含期望的关键词
    """
    # expected = test_case.get("expected", "").lower()
    # response = response.lower()
    #
    # # 简单的关键词匹配评分
    # keywords = expected.split()
    # score = sum(1 for keyword in keywords if keyword in response) / len(keywords)
    score = 0.0
    expected = str(test_case.get("expected", ""))
    if response == expected:
        score = 1.0
    return score


def test_optimizer():
    """
    测试优化器函数 - 根据优化器结合具体场景进行优化
    """
    file_path = '生成式搜索问题测评集-20250414.xlsx'
    sheet_name = '明细查询-薪资场景'

    test_dataset = []

    try:
        test_dataset = read_questions_and_units(file_path, sheet_name)
        print("读取结果：")
        for item in test_dataset:
            print(item)
    except Exception as e:
        print(f"读取文件时出错: {e}")

    # 优化和反思的大模型
    optimize_llm_config = LLM_Config(
        model_name="qwen-plus",
        api_key="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    # 测试数据集的大模型
    test_llm_config = LLM_Config(
        model_name="qwen2.5-32b-instruct",
        api_key="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    current_time = datetime.now().strftime("%Y%m%d %H:%M:%S")

    initial_prompt = test_prompt.format(
            current_time=current_time
    )

    # 创建优化器实例
    optimizer = PromptOptimizer(optimize_llm_config=optimize_llm_config, test_llm_config=test_llm_config)

    # 优化建议
    optimize_suggestion = '''
1. 针对模糊时间范围的解析，例如“最近三年”或“近五年”，明确起始时间为当前年份减去指定年数加一，并确保输出格式为YYYY。  
2. 对于“这些年来”、“这些年”等模糊表达，统一解释为当前年份减去5年，并以年份格式（YYYY）输出。  
3. 在处理“前年”、“去年”等相对时间词时，结合当前时间动态计算对应的起始时间，避免直接输出错误月份信息。  
4. 强化对“半年”、“季度”等短时间跨度的语义理解，确保准确提取起始月份并遵循YYYYMM格式输出。  
5. 优化对“上半年”、“本年度前半段”等具体时间段的解析规则，统一将起始时间设定为当年1月（YYYY01）。  
6. 对于“自前年以来”的表达，明确识别“前年”为当前年份减2年，并以年份格式（YYYY）输出起始时间。  
7. 在处理“近几个年度”时，将其默认解释为当前年份减去3年，并以年份格式（YYYY）输出起始时间。  
8. 对“今年”的查询，统一输出当前年份的一月（YYYY01），避免因月份推算导致歧义。  
9. 针对“上一季度”的查询，确保正确判断当前季度并回溯至上一季度的起始月份（YYYYMM）。  
10. 增强对“两年”、“三年”等固定时间跨度的解析能力，确保起始时间计算准确且符合规则要求。
    '''

    # 运行优化
    result = optimizer.optimize(
        initial_prompt=initial_prompt,
        test_dataset=test_dataset,
        evaluation_func=example_evaluation_func,
        optimize_suggestion=None  #若初始提示词，该参数为None
    )

    print(f"最佳提示词:\n{result['optimize_prompt']}")
    print(f"耗费token:\n{result['total_tokens']}")

    # 保存所有结果
    with open("../../results/optimization_results_start_time.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


def read_questions_and_units(file_path: str, sheet_name: str) -> list:
    """
    读取 Excel 文件指定 sheet 中的“用户问题”和“时间度量单位”两列，
    并将数据转换为 list[dict] 格式。

    :param file_path: Excel 文件路径
    :param sheet_name: 需要读取的 sheet 名称
    :return: 返回 list，每个元素为字典，字典中的 'input' 对应用户问题，'expected' 对应时间度量单位
    """
    # 读取 Excel 文件中指定 sheet 的内容
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # 检查是否包含必要的列
    if '用户问题' not in df.columns or '起始时间' not in df.columns:
        raise ValueError("Excel 中未找到 '用户问题' 或 '起始时间' 列，请检查表头名称。")

    # 定义转换函数
    # def transform_unit(unit):
    #     if unit == "年":
    #         return "0310"
    #     elif unit == "月":
    #         return "0307"
    #     else:
    #         # 如果有其他单位，这里也可以添加对应转换逻辑或直接返回原值
    #         return unit

    # 使用 apply 将每一行转换为字典，然后转换为 list
    result = df.apply(lambda row: {
        "input": row["用户问题"],
        "expected": row["起始时间"]
    }, axis=1).tolist()

    return result


def main():
    # 运行多模型测试
    test_optimizer()


if __name__ == "__main__":
    main()
