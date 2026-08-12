import os
from google import genai
from dotenv import load_dotenv

load_dotenv()


class GeminiProvider:
    def __init__(self) -> None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured")
        self.model = os.environ.get("GEMINI_MODEL", "gemini-3.1-pro-preview")
        self.client = genai.Client(api_key=api_key)

    def generate(self, input_text: str) -> str:
        interaction = self.client.interactions.create(
            model=self.model,
            input=input_text,
            generation_config={
                "thinking_level": "high",
                "temperature": 1.0,
                "max_output_tokens": 65536,
                "top_p": 0.95,
            },
        )
        return interaction.output_text
