from uuid import uuid4

from app.memory.short_term import InMemoryStore
from app.providers.gemini import GeminiProvider
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry


class AgentRuntime:
    """Agent runtime with sessions, provider abstraction, and tool execution."""

    def __init__(
        self,
        provider: GeminiProvider | None = None,
        memory: InMemoryStore | None = None,
        tools: ToolRegistry | None = None,
    ) -> None:
        self.provider = provider or GeminiProvider()
        self.memory = memory or InMemoryStore()
        self.tools = tools or ToolRegistry()
        self.tool_executor = ToolExecutor(self.tools)

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
