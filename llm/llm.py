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

    def generate_response(self, messages: list) -> Tuple[str, int]:
        """
        调用大模型，生成非流式结果
        :param messages:
        :return:
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                # 此处以qwen-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
                messages=messages,
                # [
                #     {'role': 'user', 'content': prompt}
                # ],
            )

            return response.choices[0].message.content, response.usage.total_tokens
        except Exception as e:
            print(f"Error generating response: {e}")
            return "", 0

    def generate_response_stream(self, messages: list) -> Tuple[str, int]:
        """
        调用大模型，生成流式结果
        :param messages:
        :return:
        """
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                stream=True,
                stream_options={"include_usage": True},
                # extra_body={"enable_thinking": True},
            )

            response = ""
            total_tokens = 0
            for chunk in completion:
                if len(chunk.choices) > 0 and chunk.choices[0].finish_reason != "stop":
                    content = chunk.choices[0].delta.content
                    response += content
                    print(content, end='', flush=True)  # 流式打印
                elif "usage" in chunk and chunk.usage:
                    total_tokens = chunk.usage.total_tokens

            return response, total_tokens
        except Exception as e:
            print(f"Error generating response: {e}")
            return "", 0

    def generate_response_test_connect(self) -> tuple[bool, str]:
        """
        调用大模型，生成非流式结果
        :param messages:
        :return:
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                # 此处以qwen-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
                messages=
                [
                    {'role': 'system', 'content': "ping"}
                ],
                max_tokens=1
            )
            msg = ""
            if response.choices[0].message.content:
                return True, msg
            else:
                return False, response.error_message
        except Exception as e:
            print(f"Error generating response: {e}")
            return False, str(e)
