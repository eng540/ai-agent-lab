import pytest

from app.tools.base import Tool
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry


def test_tool_registry_and_executor():
    registry = ToolRegistry()
    registry.register(Tool(name="add", description="Add numbers", handler=lambda a, b: a + b))
    executor = ToolExecutor(registry)
    assert executor.execute("add", {"a": 2, "b": 3}) == 5


def test_confirmation_required():
    registry = ToolRegistry()
    registry.register(Tool(name="danger", description="Protected", handler=lambda: "ok", requires_confirmation=True))
    executor = ToolExecutor(registry)
    with pytest.raises(PermissionError):
        executor.execute("danger", {})
    assert executor.execute("danger", {}, confirmed=True) == "ok"
