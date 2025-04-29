class LLM_Config:
    def __init__(
        self,
        model_name: str,
        api_key: str,
        base_url: str
    ):
        """
        初始化提示词优化器

        Args:
            model_name: 模型名称
            api_key: API密钥
            base_url: API基础URL
        """
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url
