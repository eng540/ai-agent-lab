from fastapi import FastAPI
from pydantic import BaseModel
from agents import Runner

from agent import agent


app = FastAPI(title="AI Agent Lab")


class AskRequest(BaseModel):
    message: str


@app.get("/")
def health():
    return {
        "status": "ok",
        "service": "AI Agent Lab"
    }


@app.post("/ask")
async def ask(request: AskRequest):
    result = await Runner.run(
        agent,
        request.message
    )

    return {
        "answer": result.final_output
    }
