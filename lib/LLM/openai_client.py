from openai import OpenAI
from dotenv import load_dotenv
import os
from typing import List

class OpenAIClient:
    def __init__(self) -> None:
        self.openai_client = None

    def load_env(self):
        ENV_DIR = os.path.dirname(os.path.abspath(__file__))
        load_dotenv(os.path.join(ENV_DIR, ".env"))

    def initialize_openai_client(self) -> None:
        self.load_env()
        self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    def chat(self, system:str, prompts:List[str]) -> str:
        messages = [{"role": "system", "content": system}]
        for prompt in prompts:
            messages.append({"role": "user", "content": prompt})
        msg = self.chat_completion(messages)
        return msg

    def chat_completion(self, messages) -> str:
        chat_completion = self.openai_client.chat.completions.create(
            # model="gpt-4-1106-preview",
            model="gpt-3.5-turbo-1106",
            response_format={ "type": "json_object" },
            messages=messages
        )
        return chat_completion.choices[0].message.content
