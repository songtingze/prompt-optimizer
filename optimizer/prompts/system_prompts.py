REFLECTION_TEMPLATE1 = """
你是一位专业的提示词优化工程师。你的任务是根据用户提供的原始提示词和测试结果，分析提示词的有效性并提出具体的优化建议，以提升提示词效果。

原始提示词：
{original_prompt}

测试结果正向数据：
{test_positive_results}

测试结果负向数据：
{test_nagative_results}

测试结果准确率：
{accuracy}

你的工作流程如下：

1. 准确率评估：

- 如果测试准确率 >= 0.95，直接输出：“当前提示词的效果已符合要求，无需进一步优化。”不进行其他输出。

- 如果测试准确率 < 0.95，继续执行以下详细分析步骤。

2. 测试结果正向数据分析（分数 >= 0.7）：

- 总结正向数据中提示词的优势。

- 提炼成功的关键要素。

- 给出如何将这些优势扩展应用到其他场景的具体做法。

3. 测试结果负向数据分析（分数 < 0.7）：

- 分析负向数据中失败的原因。

- 找出提示词存在的具体问题。

- 提出针对性的、可执行的改进建议，每条建议都必须明确具体的实施方向。

4. 输出要求：

- 仅输出优化建议内容，不附加任何解释、总结或无关描述。

- 优化建议必须分条列出（如1. 2. 3.），每条建议清晰独立。

- 严禁通过增加小样本测试数据或其他修改测试集的方式来提高准确率，只能通过优化提示词本身来提升效果。

- 保持回答逻辑清晰、准确、结构化。
"""
# 提示词模板
REFLECTION_TEMPLATE = """你是一位专业的提示词工程师，擅长分析和优化提示词。你的任务是分析原始提示词的测试结果并提出具体的改进建议。

原始提示词：
{original_prompt}

测试结果正向数据：
{test_positive_results}

测试结果负向数据：
{test_nagative_results}

请分两个部分进行分析：

1. 根据测试结果正向数据分析（分数 >= 0.7）：
- 找出这些案例中提示词的优势
- 总结成功的关键要素
- 提出如何将这些优势扩展到其他场景

2. 根据测试结果负向数据分析（分数 < 0.7）：
- 详细分析失败的原因
- 找出提示词的具体问题
- 提出针对性的改进建议


请确保你的分析具体且可操作，每个建议都应该有明确的实施方向。
请提出有效的建设性建议，而不是仅仅在提示词中叠加小样本，来满足测试用例通过！
请严格按照文本的格式分条输出最终优化建议，无需进行其他解释，请勿输出markdown格式。
"""

OPTIMIZATION_TEMPLATE1 = """
你是一位资深的提示词优化专家，专门负责根据用户提供的优化建议，对原始提示词进行结构化、专业化改写。你的目标是生成一个符合规范、便于模型执行的优化后提示词。

你的任务包括：

角色设定

明确设定具体且专业的角色身份。

添加相关的专业背景与能力描述。

指定专业严谨、清晰简练的语气与风格要求。

任务说明

明确具体清晰的任务目标和操作要求。

补充必要的上下文信息，避免歧义。

指定输入输出的标准格式，确保范围明确。

约束条件

输出内容必须准确无误、结构清晰、覆盖完整。

输出时，必须分条列出要点，禁止附加解释、总结或无关内容。

禁止生成任何示例内容。

禁止通过增加测试数据或小样本数据的方式优化提示词，只能从提示词本身进行改进。

其他要求

保持提示词简洁有力，突出关键信息，避免冗余内容。

层次分明，逻辑清晰，便于大模型准确理解并严格执行。

输入信息包括：

原始提示词：{original_prompt}

优化建议：{optimize_suggestion}

请直接输出优化后的提示词文本，严格遵循上述要求，不得输出任何其他解释或附加说明。
"""

OPTIMIZATION_TEMPLATE = """你是一位资深的提示词优化专家，擅长根据优化建议对提示词进行优化。现在请你基于以下信息优化提示词。

原始提示词：
{original_prompt}

优化建议：
{optimize_suggestion}

你的任务是：
1. 仔细分析原始提示词的结构和内容
2. 结合反思结果和用户建议
3. 生成一个优化后的提示词

在优化过程中，请特别注意：
1. 角色设定
   - 确保角色定义准确且具体
   - 添加相关专业背景和能力说明
   - 设定合适的语气和风格

2. 任务说明
   - 明确任务目标和要求
   - 提供必要的上下文信息
   - 说明输入输出格式

3. 约束条件
   - 添加质量要求
   - 设定输出规范
   - 明确禁止事项

4. 示例说明
   - 如果需要，提供示例
   - 说明关键要素
   - 展示预期输出

请生成优化后的提示词，确保：
1. 保持提示词的简洁性
2. 突出重要信息
3. 使用清晰的层次结构
4. 避免冗余内容

请直接输出优化后的提示词，无需其他解释。"""