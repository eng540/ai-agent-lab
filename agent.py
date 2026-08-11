import os
from google import genai


client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)


def run_agent(message: str) -> str:
    interaction = client.interactions.create(
        model="gemini-3.1-pro-preview",
        input=message,
        generation_config={
            "thinking_level": "high",
            "temperature": 1,
            "max_output_tokens": 65536,
            "top_p": 0.95,
        },
    )

    return interaction.output_text
