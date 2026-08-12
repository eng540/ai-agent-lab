from fastapi import APIRouter, HTTPException

from app.agent.runtime import AgentRuntime
from app.schemas.agent import AgentResponse, AskRequest

router = APIRouter()
runtime = AgentRuntime()


@router.get("/")
def health():
    return {"status": "ok", "service": "AI Agent Lab", "version": "2.0.0"}


@router.post("/ask", response_model=AgentResponse)
def ask(request: AskRequest):
    try:
        return runtime.run(request.message, request.session_id)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Agent provider request failed") from exc
