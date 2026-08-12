from pydantic import BaseModel, Field
from typing import Any, Literal


class AskRequest(BaseModel):
    message: str = Field(min_length=1, max_length=20000)
    session_id: str | None = Field(default=None, max_length=128)


class AgentResponse(BaseModel):
    answer: str
    session_id: str
    run_id: str
    model: str
    steps: int = 1
    tool_calls: list[dict[str, Any]] = []
    status: Literal["completed", "failed"] = "completed"
