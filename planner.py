import json
import os
import time

from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
MODEL_ID = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
MAX_RETRIES = int(os.environ.get("GEMINI_MAX_RETRIES", "2"))
RETRY_BASE_SECONDS = float(os.environ.get("GEMINI_RETRY_BASE_SECONDS", "2"))

PLANNER_INSTRUCTION = """
You are a task planner. Convert the user's request into a short executable plan.
Return ONLY valid JSON with this shape:
{"goal":"...","steps":[{"id":"step-1","description":"...","verification":"..."}]}
Use 1-4 steps. Do not invent capabilities. Available capabilities are:
list/read/write files and project status in the workspace.
"""


def _generate(contents: str):
    last_exc = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            return client.models.generate_content(
                model=MODEL_ID,
                contents=contents,
                config={"temperature": 0.1, "max_output_tokens": 1536},
            )
        except Exception as exc:
            last_exc = exc
            text = str(exc).lower()
            retryable = any(x in text for x in ("429", "rate limit", "resource_exhausted", "too many requests", "quota"))
            if not retryable or attempt >= MAX_RETRIES:
                raise
            time.sleep(RETRY_BASE_SECONDS * (2 ** attempt))
    raise last_exc


def create_plan(message: str) -> dict:
    response = _generate(f"{PLANNER_INSTRUCTION}\n\nUser task:\n{message}")
    text = response.text.strip()
    if text.startswith("```"):
        text = text.strip("`").replace("json\n", "", 1).strip()
    plan = json.loads(text)
    if not isinstance(plan.get("steps"), list) or not plan["steps"]:
        raise ValueError("Planner returned an empty plan")
    return plan
