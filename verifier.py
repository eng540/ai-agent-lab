import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
MODEL_ID = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")


def verify_task(goal: str, results: list[dict]) -> dict:
    summary = "\n".join(f"{r['step_id']} [{r['status']}]: {r['result']}" for r in results)
    prompt = f"""
Verify whether this task was completed based ONLY on the execution results below.
Return concise JSON only:
{{"status":"passed|failed|partial","reason":"...","next_action":"..."}}
Goal: {goal}
Execution results:
{summary}
"""
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config={"temperature": 0.0, "max_output_tokens": 1024},
    )
    import json
    text = response.text.strip().strip("`").replace("json\n", "", 1).strip()
    return json.loads(text)
