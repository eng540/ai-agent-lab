from typing import Any

from app.tools.registry import ToolRegistry


class ToolExecutor:
    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry

    def execute(self, name: str, arguments: dict[str, Any], *, confirmed: bool = False) -> Any:
        tool = self.registry.get(name)
        if tool.requires_confirmation and not confirmed:
            raise PermissionError(f"Tool requires confirmation: {name}")
        return tool.execute(arguments)
