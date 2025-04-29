from typing import Tuple

from openai import OpenAI


class LLM:
    """
    模型参数配置类，用于加载大模型所需的配置参数。
    """

    def __init__(self, api_key: str, base_url: str, model_name: str):
        """
        初始化模型参数

        :param api_key: api_key
        :param base_url: base_url
        :param model_name: 模型名称
        """
        # self.api_key = api_key
        # self.base_url = base_url
        self.model_name = model_name
        self.client = OpenAI(
            # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
            api_key=api_key,
            base_url=base_url,
        )

    def generate_response(self, prompt: str) -> Tuple[str, int]:
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                # 此处以qwen-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
                messages=[
                    {'role': 'user', 'content': prompt}
                ],
                # max_tokens= kwargs.get("max_tokens", self.model_config["max_tokens"]),
                # temperature= kwargs.get("temperature", self.model_config["temperature"]),
                # top_p= kwargs.get("top_p", self.model_config["top_p"]),
                # result_format= self.model_config["result_format"]
            )

            return response.choices[0].message.content, response.usage.total_tokens
        except Exception as e:
            print(f"Error generating response: {e}")
            return "", 0

    def generate_response_with_system_prompt(self, system_prompt: str, user_prompt: str) -> Tuple[str, int]:
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                # max_tokens= kwargs.get("max_tokens", self.model_config["max_tokens"]),
                # temperature= kwargs.get("temperature", self.model_config["temperature"]),
                # top_p= kwargs.get("top_p", self.model_config["top_p"]),
                # result_format= self.model_config["result_format"]
            )

            return response.choices[0].message.content, response.usage.total_tokens
        except Exception as e:
            print(f"Error generating response: {e}")
            return "", 0
