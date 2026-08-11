from fastapi import FastAPI
from pydantic import BaseModel

from agent import run_agent


app = FastAPI(
    title="AI Agent Lab",
    version="0.2.0",
)


class AskRequest(BaseModel):
    message: str


@app.get("/")
def health():
    return {
        "status": "ok",
        "service": "AI Agent Lab",
        "version": "0.2.0",
    }


@app.post("/ask")
def ask(request: AskRequest):
    answer = run_agent(request.message)

    return {
        "answer": answer
    }
