from fastapi import FastAPI
from pydantic import BaseModel
from agent import run_agent

app = FastAPI(
    title="AI Agent Lab",
    version="1.2.0",
)


class AskRequest(BaseModel):
    message: str


@app.get("/")
def health():
    return {
        "status": "ok",
        "service": "AI Agent Lab",
        "version": "1.2.0",
        "capabilities": ["chat", "tools", "workspace", "multi_step_execution", "verification"],
    }


@app.post("/ask")
def ask(request: AskRequest):
    return {"answer": run_agent(request.message)}
