from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agent import run_agent
from tools.files import list_files

app = FastAPI(title="AI Agent Lab", version="1.3.0")
app.mount("/static", StaticFiles(directory="static"), name="static")

class AskRequest(BaseModel):
    message: str

@app.get("/", include_in_schema=False)
def home():
    return FileResponse("static/index.html")

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "AI Agent Lab",
        "version": "1.3.0",
        "capabilities": ["chat", "tools", "workspace", "multi_step_execution", "verification", "web_console"],
    }

@app.get("/workspace/files")
def workspace_files():
    return {"files": list_files(".")}

@app.post("/ask")
def ask(request: AskRequest):
    return {"answer": run_agent(request.message)}
