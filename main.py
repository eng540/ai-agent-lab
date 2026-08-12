from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from planner import create_plan
from executor import execute_plan
from verifier import verify_task
from task_store import add_event, create_task, get_task, recent_tasks, update_task
from tools.files import list_files

app = FastAPI(title="AI Agent Lab", version="1.5.0")
app.mount("/static", StaticFiles(directory="static"), name="static")

class AskRequest(BaseModel):
    message: str
    mode: str = "autonomous"

@app.get("/", include_in_schema=False)
def home():
    return FileResponse("static/index.html")

@app.get("/health")
def health():
    return {"status":"ok","service":"AI Agent Lab","version":"1.5.0","capabilities":["planner","executor","tools","workspace","verification","task_history","web_console"]}

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

@app.post("/plan")
def plan(request: AskRequest):
    return create_plan(request.message)

@app.post("/ask")
def ask(request: AskRequest):
    task = create_task(request.message)
    update_task(task["id"], status="planning", mode=request.mode)
    add_event(task["id"], "planning", "إنشاء خطة تنفيذ")

    def event_callback(event, detail=None):
        add_event(task["id"], event, detail)

    try:
        plan_data = create_plan(request.message)
        update_task(task["id"], plan=plan_data, status="running")
        add_event(task["id"], "plan_created", plan_data)
        results = execute_plan(plan_data, event_callback=event_callback)
        update_task(task["id"], results=results)
        verification = verify_task(plan_data["goal"], results)
        update_task(task["id"], verification=verification)
        add_event(task["id"], "verification", verification)
        status = verification.get("status", "partial")
        update_task(task["id"], status="completed" if status == "passed" else status)
        answer = f"تم تنفيذ الخطة. حالة التحقق: {status}.\n\n" + "\n".join(r["result"] for r in results)
        update_task(task["id"], answer=answer)
        return {"task_id": task["id"], "plan": plan_data, "results": results, "verification": verification, "answer": answer}
    except Exception as exc:
        add_event(task["id"], "failed", str(exc))
        update_task(task["id"], status="failed", answer=f"حدث خطأ أثناء تنفيذ المهمة: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))
