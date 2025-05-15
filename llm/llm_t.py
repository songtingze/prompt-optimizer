import json
from typing import Tuple
from utils.logger import logger
from openai import OpenAI
import requests

class LLM:
    """
    模型参数配置类，用于加载大模型所需的配置参数。
    """

    def __init__(self, api_key: str, base_url: str, model_name: str, temperature: float):
        """
        初始化模型参数

        :param api_key: api_key
        :param base_url: base_url
        :param model_name: 模型名称
        :param temperature: 模型temperature
        """
        # self.api_key = api_key
        # self.base_url = base_url
        self.temperature = temperature
        self.model_name = model_name
        self.client = OpenAI(
            # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
            api_key=api_key,
            base_url=base_url,
        )

    def generate_response(self, prompt: str) -> Tuple[str, int]:
        """
        调用大模型，生成非流式结果
        :param messages:
        :return:
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                # 此处以qwen-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
                messages=[
                    {'role': 'user', 'content': prompt}
                ],
                # max_tokens= kwargs.get("max_tokens", self.model_config["max_tokens"]),
                temperature=self.temperature
                # top_p= kwargs.get("top_p", self.model_config["top_p"]),
                # result_format= self.model_config["result_format"]
            )

            return response.choices[0].message.content, response.usage.total_tokens
        except Exception as e:
            print(f"Error generating response: {e}")
            return "", 0


    # 适用测试环境的行内大模型接口
    def request_ry_llm(self, prompt_text, model_name, chat_id, variable_text = "", prod=False):
        if prod:
            url = "xxxxxxxxxxxxxxxx"
        else:
            url = ""

        request_data = {
            "txHeader":{},
            "txBody":{

            }
        }
        headers = {
            "Content-type":"application/json"
        }
        try:
            ret = requests.post(url, json=request_data, headers=headers)
            response_json = json.load(ret.text)
            response_text = response_json["txBody"]["txEntity"]["choices"][0]["message"]["content"]
            logger.info("大模型接口返回:%s",response_json)
        except Exception as e:
            logger.error(f"A LLM error occurred:{e}")
        return response_text
