from fastapi import APIRouter, HTTPException

from app.agent.runtime import AgentRuntime
from app.schemas.agent import AgentResponse, AskRequest

router = APIRouter()
runtime = AgentRuntime()


@router.get("/")
def health():
    return {"status": "ok", "service": "AI Agent Lab", "version": "3.0.0"}


@router.get("/tools")
def tools():
    return {
        "tools": [
            {
                "name": tool.name,
                "description": tool.description,
                "requires_confirmation": tool.requires_confirmation,
            }
            for tool in runtime.tools.list()
        ]
    }


@router.post("/ask", response_model=AgentResponse)
def ask(request: AskRequest):
    try:
        return runtime.run(request.message, request.session_id)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Agent runtime request failed") from exc
