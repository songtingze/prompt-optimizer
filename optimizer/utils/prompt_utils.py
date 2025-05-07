from pathlib import Path



class PromptUtils:
    def __init__(self, root_path: Path):
        self.root_path = root_path

    def create_round_directory(self, prompt_path: Path, round_number: int) -> Path:
        directory = prompt_path / f"round_{round_number}"
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    def load_prompt(self, round_number: int, prompts_path: Path):
        prompt_file = prompts_path / "prompt.txt"

        try:
            return prompt_file.read_text(encoding="utf-8")
        except FileNotFoundError as e:
            # logger.info(f"Error loading prompt for round {round_number}: {e}")
            print((f"Error loading prompt for round {round_number}: {e}"))
            raise

    def write_answers(self, directory: Path, success: bool, modification_all: str, answers: dict, name: str = "answers.txt"):
        answers_file = directory / name
        with answers_file.open("w", encoding="utf-8") as file:
            file.write(f"当前轮次的优化结果为：{success}\n")
            file.write("\n")
            file.write(f"当前轮次得到的LLM思考反馈结果为：{modification_all}\n")
            file.write("\n")
            file.write("当前轮次得到的最新prompt执行结果为：\n")
            for item in answers:
                file.write(f"Question:\n{item['question']}\n")
                file.write(f"Answer:\n{item['answer']}\n")
                file.write("\n")

    def write_prompt(self, directory: Path, prompt: str):
        prompt_file = directory / "prompt.txt"
        prompt_file.write_text(prompt, encoding="utf-8")
