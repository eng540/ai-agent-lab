import json
import logging
import os
import time
from typing import Any

from dotenv import load_dotenv
from google import genai

from tools.files import list_files, read_file, write_file
from tools.project import project_status

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai-agent-lab")

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
MODEL_ID = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
THINKING_LEVEL = os.environ.get("GEMINI_THINKING_LEVEL", "low")
MAX_TOOL_ROUNDS = int(os.environ.get("MAX_TOOL_ROUNDS", "4"))
MAX_RETRIES = int(os.environ.get("GEMINI_MAX_RETRIES", "2"))
RETRY_BASE_SECONDS = float(os.environ.get("GEMINI_RETRY_BASE_SECONDS", "2"))

TOOLS = [
    {"type": "function", "name": "list_files", "description": "List files inside the agent workspace.", "parameters": {"type": "object", "properties": {"relative_dir": {"type": "string"}}}},
    {"type": "function", "name": "read_file", "description": "Read a UTF-8 text file from the agent workspace.", "parameters": {"type": "object", "properties": {"relative_path": {"type": "string"}}, "required": ["relative_path"]}},
    {"type": "function", "name": "write_file", "description": "Create or replace a UTF-8 text file inside the agent workspace.", "parameters": {"type": "object", "properties": {"relative_path": {"type": "string"}, "content": {"type": "string"}}, "required": ["relative_path", "content"]}},
    {"type": "function", "name": "project_status", "description": "Return workspace status and file inventory.", "parameters": {"type": "object", "properties": {}}},
]
TOOL_FUNCTIONS = {"list_files": list_files, "read_file": read_file, "write_file": write_file, "project_status": project_status}

SYSTEM_INSTRUCTION = """
You are AI Agent Lab, an execution-oriented agent.
When a request requires work, inspect the workspace, choose tools, execute the task,
verify important outputs, and report what was actually done.
Never pretend an action happened. Only use the provided workspace tools.
Inspect relevant files before conclusions. After creating an important file, read it back.
Keep tool use focused and stop when the objective is complete.
"""


def _generation_config() -> dict[str, Any]:
    level = THINKING_LEVEL.lower().strip()
    if level not in {"low", "high"}:
        level = "low"
    return {"thinking_level": level, "temperature": 0.2, "max_output_tokens": 4096}


def _is_retryable(exc: Exception) -> bool:
    text = str(exc).lower()
    return any(x in text for x in ("429", "rate limit", "resource_exhausted", "too many requests", "quota"))


def _create_interaction(**kwargs):
    last_exc = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            return client.interactions.create(**kwargs)
        except Exception as exc:
            last_exc = exc
            if not _is_retryable(exc) or attempt >= MAX_RETRIES:
                raise
            delay = RETRY_BASE_SECONDS * (2 ** attempt)
            logger.warning("Gemini quota/rate limit; retrying in %.1fs", delay)
            time.sleep(delay)
    raise last_exc


def _execute_tool(name: str, arguments: dict):
    if name not in TOOL_FUNCTIONS:
        raise ValueError(f"Unknown tool: {name}")
    return TOOL_FUNCTIONS[name](**arguments)


def run_agent(message: str, event_callback=None) -> str:
    def emit(event, detail=None):
        logger.info("[EVENT] %s %s", event, detail or "")
        if event_callback:
            event_callback(event, detail)

    try:
        emit("planning", "بدأ تحليل المهمة")
        interaction = _create_interaction(
            model=MODEL_ID,
            input=message,
            tools=TOOLS,
            system_instruction=SYSTEM_INSTRUCTION,
            generation_config=_generation_config(),
        )

        for round_number in range(1, MAX_TOOL_ROUNDS + 1):
            calls = [step for step in interaction.steps if step.type == "function_call"]
            if not calls:
                emit("completed", "اكتملت المهمة")
                return interaction.output_text or "تمت المهمة دون نص إضافي."

            emit("tool_round", f"الجولة {round_number}")
            results = []
            for call in calls:
                emit("tool_started", call.name)
                try:
                    result = _execute_tool(call.name, call.arguments or {})
                    payload = {"ok": True, "result": result}
                    emit("tool_succeeded", call.name)
                except Exception as exc:
                    payload = {"ok": False, "error": str(exc)}
                    emit("tool_failed", f"{call.name}: {exc}")
                results.append({
                    "type": "function_result",
                    "name": call.name,
                    "call_id": call.id,
                    "result": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False)}],
                })

            interaction = _create_interaction(
                model=MODEL_ID,
                previous_interaction_id=interaction.id,
                input=results,
                tools=TOOLS,
                system_instruction=SYSTEM_INSTRUCTION,
                generation_config=_generation_config(),
            )

        emit("stopped", "تم بلوغ الحد الآمن لجولات الأدوات")
        return "توقفت المهمة بعد بلوغ الحد الآمن لعدد جولات الأدوات."
    except Exception as exc:
        emit("failed", str(exc))
        logger.exception("[AGENT] Request failed")
        return f"حدث خطأ أثناء تنفيذ المهمة: {exc}"
