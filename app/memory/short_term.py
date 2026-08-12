from dataclasses import dataclass, field
from threading import Lock


@dataclass
class SessionMemory:
    messages: list[dict[str, str]] = field(default_factory=list)


class InMemoryStore:
    """Small V2 session store; replaceable by Redis/DB later."""

    def __init__(self, max_messages: int = 20):
        self._sessions: dict[str, SessionMemory] = {}
        self._lock = Lock()
        self.max_messages = max_messages

    def get(self, session_id: str) -> SessionMemory:
        with self._lock:
            return self._sessions.setdefault(session_id, SessionMemory())

    def append(self, session_id: str, role: str, content: str) -> None:
        with self._lock:
            session = self._sessions.setdefault(session_id, SessionMemory())
            session.messages.append({"role": role, "content": content})
            session.messages = session.messages[-self.max_messages :]
