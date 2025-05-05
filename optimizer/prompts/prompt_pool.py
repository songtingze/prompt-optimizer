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
