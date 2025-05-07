EVALUATE_PROMPT = """
根据原始要求，评估A和B两组prompt和答案，并确定哪一组更符合要求。如果提供了参考示例，请严格遵守参考答案示例的格式/内容。（当有一项为空时，直接选择非空项）
# 要求
{requirement}

# A
{sample}

# B
{new_sample}

# 参考示例
{answers}

使用 XML 标记封装您的回答，提供您的分析、优化点和您认为更好的选择。

<analyse>综合分析参考示例和目前根据prompt提示产生的结果存在哪些缺点，以及下一步应该如何改进prompt提示。</analyse>
<modification>简要概括缺点和需要改进的要点。</modification>
<choose>A/B (我认为的更好的回答)</choose>
"""

PROMPT_OPTIMIZE_PROMPT = """
你现在生成一个新的prompt，以满足用户的需求(requirement)。根据LLM的评估反馈和人类用户的评估反馈，对当前给定的参考的prompt进行重构和优化。你可以添加、修改或删除prompt。请在回复中使用规定的XML格式。
在优化过程中，你可以融合任意的思考模型（thinking models）。当前参考的prompt为上一个迭代中表现最出色的prompt，你必须在该prompt的基础上进行进一步的优化和改进。修改后的prompt必须和提供的参考prompt不同。

需求:
```
{requirements}
```

当前参考的prompt:
```
{prompt}
```

该参考的prompt的执行结果是（在一些示例下）：
```
{answers}
```

来自LLM的优化反馈，包含大模型评估的当前prompt的缺点和优化要点：
```
{LLM_feedback}
```

来自人类用户的优化反馈，包含用户自行分析的当前prompt的缺点和优化要点：
```
{human_feedback}
```

我们期待的最佳答案（在一些示例下）:
```
{golden_answers}
```

使用以下XML格式提供你根据来自LLM和人类两个途径的优化反馈生成的，完整的优化后的prompt：

<prompt>提供完整的优化后的prompt {count}</prompt>
"""
