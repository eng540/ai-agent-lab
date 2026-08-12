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
    task = {"id": uuid.uuid4().hex[:10], "message": message, "status": "queued", "created_at": _now(), "events": [], "answer": None}
    with LOCK:
        items = _load()
        items.append(task)
        _save(items)
    return task


def get_task(task_id):
    with LOCK:
        return next((x for x in _load() if x["id"] == task_id), None)


def recent_tasks():
    with LOCK:
        return list(reversed(_load()[-30:]))


def update_task(task_id, **fields):
    with LOCK:
        items = _load()
        for item in items:
            if item["id"] == task_id:
                item.update(fields)
                break
        _save(items)


def add_event(task_id, event, detail=None):
    with LOCK:
        items = _load()
        for item in items:
            if item["id"] == task_id:
                item.setdefault("events", []).append({"time": _now(), "event": event, "detail": detail})
                break
        _save(items)
