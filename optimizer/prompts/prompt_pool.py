EVALUATE_PROMPT = """
根据原始要求，评估A和B两组prompt和答案，并确定哪一组更符合要求。如果提供了参考示例，请严格遵守参考答案示例的格式/内容。（当有一项为空时，直接选择非空项）

# A
{sample}

# B
{new_sample}

# 参考示例
{answers}

思考过程：
1.根据示例的问答对进行分析，A和B哪组的答案更准确，答案更准确的为优胜组，反之为失败组；
2.分析失败组的失败原因，产生答案的prompt存在哪些问题，有哪些优点；
3.分析优胜组的prompt，可以参考失败组prompt分析进行综合优化，分析出优胜组的prompt还存在的缺点，以及下一步的优化可以如何改进。

使用 XML 标记封装您的回答，提供您的缺点分析、优化点和您认为更好的选择。
<analyse>综合分析得出的目前优胜者的prompt提示产生的结果还存在哪些缺点。</analyse>
<modification>优胜者的prompt仍需要改进的要点。</modification>
<choose>A/B (我认为的更好的优胜者答案)</choose>
"""

PROMPT_OPTIMIZE_PROMPT = """
你现在生成一个新的prompt，以满足用户的需求。根据LLM的评估反馈和人类用户的评估反馈，对当前给定的参考的prompt进行重构和优化。你可以添加、修改或删除prompt。请在回复中使用规定的XML格式。
在优化过程中，你可以融合任意的思考模型（thinking models）。当前参考的prompt为上一个迭代中表现最出色的prompt，你必须在该prompt的基础上进行进一步的优化和改进。修改后的prompt必须和提供的参考prompt不同。

一、当前参考的prompt:
```
{prompt}
```

二、该参考的prompt的执行结果是（在一些示例下）：
```
{answers}
```

三、来自LLM和人类的优化反馈，包含大模型评判与人类修改后共同评估的当前prompt的缺点和优化要点：
1. 当前prompt的缺点：
```
{anaysis_all}
```
2. 当前prompt的优化要点：
```
{modification_all}
```


四、我们期待的最佳答案（在一些示例下）:
```
{golden_answers}
```

五、大模型需要针对问题回答的答案：
使用以下XML格式提供你根据来自LLM和人类的优化反馈生成的，完整的优化后的prompt：

<prompt>提供完整的优化后的prompt {count}</prompt>
"""
