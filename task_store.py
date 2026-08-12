import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

STORE = Path(__file__).resolve().parent / "workspace" / "tasks" / "tasks.json"
LOCK = threading.Lock()


def _now():
    return datetime.now(timezone.utc).isoformat()


def _load():
    if not STORE.exists():
        return []
    try:
        return json.loads(STORE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _save(items):
    STORE.parent.mkdir(parents=True, exist_ok=True)
    STORE.write_text(json.dumps(items[-100:], ensure_ascii=False, indent=2), encoding="utf-8")


def create_task(message):
    task = {"id": uuid.uuid4().hex[:10], "message": message, "status": "queued", "events": [], "answer": None, "created_at": _now()}
    with LOCK:
        items = _load(); items.append(task); _save(items)
    return task


def update_task(task_id, **changes):
    with LOCK:
        items = _load()
        for task in items:
            if task["id"] == task_id:
                task.update(changes)
                break
        _save(items)


def add_event(task_id, event, detail=None):
    with LOCK:
        items = _load()
        for task in items:
            if task["id"] == task_id:
                task.setdefault("events", []).append({"time": _now(), "event": event, "detail": detail})
                break
        _save(items)


def get_task(task_id):
    with LOCK:
        task = next((x for x in _load() if x["id"] == task_id), None)
        return dict(task) if task else None


def recent_tasks(limit=20):
    with LOCK:
        return list(reversed(_load()[-limit:]))
