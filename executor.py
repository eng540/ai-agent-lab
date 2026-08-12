from dataclasses import dataclass
from typing import Callable

from agent import run_agent

@dataclass
class StepResult:
    step_id: str
    description: str
    status: str
    result: str


def execute_plan(plan: dict, event_callback: Callable | None = None) -> list[dict]:
    results = []
    for step in plan["steps"]:
        step_id = step.get("id", f"step-{len(results)+1}")
        description = step["description"]
        if event_callback:
            event_callback("step_started", f"{step_id}: {description}")
        result = run_agent(
            f"Execute ONLY this planned step:\n{description}\n"
            f"Verification requirement:\n{step.get('verification', 'Confirm the step was actually completed.')}\n"
            "Use the available workspace tools when needed. Return a concise factual result.",
            event_callback=event_callback,
        )
        failed = result.startswith("حدث خطأ") or result.startswith("توقفت المهمة")
        status = "failed" if failed else "completed"
        results.append({"step_id": step_id, "description": description, "status": status, "result": result})
        if event_callback:
            event_callback("step_completed" if not failed else "step_failed", f"{step_id}: {status}")
        if failed:
            break
    return results
