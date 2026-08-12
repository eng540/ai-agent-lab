from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agent import run_agent
from task_store import add_event, create_task, get_task, recent_tasks, update_task
from tools.files import list_files

app = FastAPI(title="AI Agent Lab", version="1.4.0")
app.mount("/static", StaticFiles(directory="static"), name="static")

class AskRequest(BaseModel):
    message: str

@app.get("/", include_in_schema=False)
def home():
    return FileResponse("static/index.html")

@app.get("/health")
def health():
    return {"status": "ok", "service": "AI Agent Lab", "version": "1.4.0", "capabilities": ["chat", "tools", "workspace", "multi_step_execution", "verification", "web_console", "task_history", "execution_events"]}

@app.get("/workspace/files")
def workspace_files():
    return {"files": list_files(".")}

@app.get("/tasks")
def tasks():
    return {"tasks": recent_tasks()}

@app.get("/tasks/{task_id}")
def task(task_id: str):
    item = get_task(task_id)
    if not item:
        raise HTTPException(status_code=404, detail="Task not found")
    return item

@app.post("/ask")
def ask(request: AskRequest):
    task = create_task(request.message)
    update_task(task["id"], status="running")
    add_event(task["id"], "started", "بدأ تنفيذ المهمة")

    def event_callback(event, detail=None):
        add_event(task["id"], event, detail)

    answer = run_agent(request.message, event_callback=event_callback)
    failed = answer.startswith("حدث خطأ")
    update_task(task["id"], status="failed" if failed else "completed", answer=answer)
    return {"task_id": task["id"], "answer": answer}
