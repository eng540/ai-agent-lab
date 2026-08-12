from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4

_tasks = {}
_lock = Lock()


def create_task(message: str) -> dict:
    task = {
        "id": str(uuid4()),
        "message": message,
        "status": "queued",
        "events": [],
        "answer": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    with _lock:
        _tasks[task["id"]] = task
    return task


def update_task(task_id: str, **changes):
    with _lock:
        if task_id in _tasks:
            _tasks[task_id].update(changes)


def add_event(task_id: str, event: str, detail=None):
    with _lock:
        if task_id in _tasks:
            _tasks[task_id]["events"].append({
                "time": datetime.now(timezone.utc).isoformat(),
                "event": event,
                "detail": detail,
            })


def get_task(task_id: str):
    with _lock:
        task = _tasks.get(task_id)
        return dict(task) if task else None


def recent_tasks(limit: int = 20):
    with _lock:
        values = list(_tasks.values())[-limit:]
        return [dict(task) for task in reversed(values)]
