from app.tools.base import Tool


def echo(text: str) -> str:
    return text


def build_default_tools() -> list[Tool]:
    return [
        Tool(
            name="echo",
            description="Return the supplied text unchanged. Safe for runtime/tool-chain tests.",
            handler=echo,
        )
    ]
