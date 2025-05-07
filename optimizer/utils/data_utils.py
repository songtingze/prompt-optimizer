import datetime
import json
from pathlib import Path
from typing import Dict, List, Union

import pandas as pd



class DataUtils:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.top_scores = {}

    def get_best_round(self):
        result_file = self.root_path / "best_results.json"
        self.top_scores = {}

        try:
            if not result_file.exists():
                print(f"Results file not found at {result_file}")
                return self.top_scores

            data = json.loads(result_file.read_text(encoding="utf-8"))

            # 直接提取字段，无需处理列表
            self.top_scores = {
                "prompt": data.get("prompt", ""),
                "answers": data.get("answers", [])
            }

        except FileNotFoundError:
            print(f"Could not find results file: {result_file}")
        except json.JSONDecodeError:
            print(f"Invalid JSON format in file: {result_file}")
        except Exception as e:
            print(f"Unexpected error loading scores: {str(e)}")

        return self.top_scores

    def create_result_data(self, answers: list[dict], prompt: str, succeed: bool, tokens: int) -> dict:
        now = datetime.datetime.now()
        return {"answers": answers, "prompt": prompt, "succeed": succeed, "tokens": tokens, "time": now}

    def get_best_results_file_path(self, prompt_path: Path) -> Path:
        return prompt_path / "best_results.json"

    def save_best_results(self, json_file_path: Path, data: Union[List, Dict]):
        # 确保目标目录存在
        json_file_path.parent.mkdir(parents=True, exist_ok=True)

        json_path = json_file_path
        json_path.write_text(json.dumps(data, default=str, indent=4))

    def list_to_markdown(self, questions_list: list):
        """
        Convert a list of question-answer dictionaries to a formatted Markdown string.

        Args:
            questions_list (list): List of dictionaries containing 'question' and 'answer' keys

        Returns:
            str: Formatted Markdown string
        """
        markdown_text = "```\n"

        for i, qa_pair in enumerate(questions_list, 1):
            # Add question section
            markdown_text += f"问题 {i}\n\n"
            markdown_text += f"{qa_pair['question']}\n\n"

            # Add answer section
            markdown_text += f"回答 {i}\n\n"
            markdown_text += f"{qa_pair['answer']}\n\n"

            # Add separator between QA pairs except for the last one
            if i < len(questions_list):
                markdown_text += "---\n\n"

        markdown_text += "\n```"

        return markdown_text