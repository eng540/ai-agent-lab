import json
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
MODEL_ID = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

PLANNER_INSTRUCTION = """
You are a task planner. Convert the user's request into a short executable plan.
Return ONLY valid JSON with this shape:
{"goal":"...","steps":[{"id":"step-1","description":"...","verification":"..."}]}
Use 1-6 steps. Do not invent capabilities. The available capabilities are:
list/read/write files and project status in the workspace.
"""

def create_plan(message: str) -> dict:
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=f"{PLANNER_INSTRUCTION}\n\nUser task:\n{message}",
        config={"temperature": 0.1, "max_output_tokens": 2048},
    )
    text = response.text.strip()
    if text.startswith("```"):
        text = text.strip("`").replace("json\n", "", 1).strip()
    plan = json.loads(text)
    if not isinstance(plan.get("steps"), list) or not plan["steps"]:
        raise ValueError("Planner returned an empty plan")
    return plan
