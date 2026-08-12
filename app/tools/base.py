from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    handler: Callable[..., Any]
    requires_confirmation: bool = False

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.handler(**arguments)
