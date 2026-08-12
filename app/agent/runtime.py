from uuid import uuid4

from app.memory.short_term import InMemoryStore
from app.providers.gemini import GeminiProvider


class AgentRuntime:
    """V2 runtime: session context + provider abstraction + run identity."""

    def __init__(self, provider: GeminiProvider | None = None, memory: InMemoryStore | None = None):
        self.provider = provider or GeminiProvider()
        self.memory = memory or InMemoryStore()

    def run(self, message: str, session_id: str | None = None) -> dict:
        session_id = session_id or uuid4().hex
        run_id = uuid4().hex
        session = self.memory.get(session_id)

        context = "\n".join(
            f"{item['role']}: {item['content']}" for item in session.messages
        )
        prompt = message if not context else (
            "Conversation context:\n" + context + "\n\nUser:\n" + message
        )

        self.memory.append(session_id, "user", message)
        answer = self.provider.generate(prompt)
        self.memory.append(session_id, "assistant", answer)

        return {
            "answer": answer,
            "session_id": session_id,
            "run_id": run_id,
            "model": self.provider.model,
            "steps": 1,
            "tool_calls": [],
            "status": "completed",
        }
