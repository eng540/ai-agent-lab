import json
import logging
import os

from dotenv import load_dotenv
from google import genai

from tools.files import list_files, read_file, write_file
from tools.project import project_status

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai-agent-lab")

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
MODEL_ID = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
MAX_TOOL_ROUNDS = 8

TOOLS = [
    {"type": "function", "name": "list_files", "description": "List files inside the agent workspace.", "parameters": {"type": "object", "properties": {"relative_dir": {"type": "string", "description": "Directory relative to workspace, usually ."}}}},
    {"type": "function", "name": "read_file", "description": "Read a UTF-8 text file from the agent workspace.", "parameters": {"type": "object", "properties": {"relative_path": {"type": "string", "description": "File path relative to workspace."}}, "required": ["relative_path"]}},
    {"type": "function", "name": "write_file", "description": "Create or replace a UTF-8 text file inside the agent workspace.", "parameters": {"type": "object", "properties": {"relative_path": {"type": "string"}, "content": {"type": "string"}}, "required": ["relative_path", "content"]}},
    {"type": "function", "name": "project_status", "description": "Return workspace status and file inventory.", "parameters": {"type": "object", "properties": {}}},
]

TOOL_FUNCTIONS = {"list_files": list_files, "read_file": read_file, "write_file": write_file, "project_status": project_status}

SYSTEM_INSTRUCTION = """
You are AI Agent Lab, an execution-oriented agent.
When a request requires work, inspect the workspace, choose tools, execute the task,
verify important outputs, and report what was actually done.

Rules:
1. Never pretend an action happened.
2. Only use the provided workspace tools for filesystem access.
3. Inspect relevant files before making project conclusions.
4. After creating an important file, read it back to verify it.
5. Keep tool use focused and stop when the objective is complete.
6. Never claim a file exists unless a tool confirms it.
"""


def _execute_tool(name: str, arguments: dict):
    if name not in TOOL_FUNCTIONS:
        raise ValueError(f"Unknown tool: {name}")
    return TOOL_FUNCTIONS[name](**arguments)


def run_agent(message: str) -> str:
    try:
        interaction = client.interactions.create(
            model=MODEL_ID,
            input=message,
            tools=TOOLS,
            system_instruction=SYSTEM_INSTRUCTION,
            generation_config={"thinking_level": "medium", "temperature": 0.2, "max_output_tokens": 8192},
        )

        for round_number in range(1, MAX_TOOL_ROUNDS + 1):
            calls = [step for step in interaction.steps if step.type == "function_call"]
            if not calls:
                return interaction.output_text or "تمت المهمة دون نص إضافي."

            results = []
            for call in calls:
                logger.info("[AGENT] Tool requested: %s %s", call.name, call.arguments)
                try:
                    result = _execute_tool(call.name, call.arguments or {})
                    payload = {"ok": True, "result": result}
                    logger.info("[TOOL] Success: %s", call.name)
                except Exception as exc:
                    payload = {"ok": False, "error": str(exc)}
                    logger.exception("[TOOL] Failed: %s", call.name)

                results.append({
                    "type": "function_result",
                    "name": call.name,
                    "call_id": call.id,
                    "result": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False)}],
                })

            logger.info("[AGENT] Tool round %s complete", round_number)
            interaction = client.interactions.create(
                model=MODEL_ID,
                previous_interaction_id=interaction.id,
                input=results,
                tools=TOOLS,
                system_instruction=SYSTEM_INSTRUCTION,
                generation_config={"thinking_level": "medium", "temperature": 0.2, "max_output_tokens": 8192},
            )

        return "توقفت المهمة بعد بلوغ الحد الآمن لعدد جولات الأدوات."
    except Exception as exc:
        logger.exception("[AGENT] Request failed")
        return f"حدث خطأ أثناء تنفيذ المهمة: {exc}"
