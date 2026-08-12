from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent / "workspace"
MAX_READ_BYTES = 512_000
MAX_WRITE_BYTES = 512_000


def _safe_path(relative_path: str) -> Path:
    candidate = (WORKSPACE / relative_path).resolve()
    workspace_root = WORKSPACE.resolve()
    if candidate != workspace_root and workspace_root not in candidate.parents:
        raise ValueError("Path is outside the workspace")
    return candidate


def list_files(relative_dir: str = ".") -> list[str]:
    directory = _safe_path(relative_dir)
    if not directory.exists():
        raise FileNotFoundError(relative_dir)
    if not directory.is_dir():
        raise ValueError(f"Not a directory: {relative_dir}")

    items: list[str] = []
    for path in sorted(directory.rglob("*")):
        if path.is_file():
            items.append(str(path.relative_to(WORKSPACE)))
    return items


def read_file(relative_path: str) -> str:
    path = _safe_path(relative_path)
    if not path.exists():
        raise FileNotFoundError(relative_path)
    if not path.is_file():
        raise ValueError(f"Not a file: {relative_path}")
    if path.stat().st_size > MAX_READ_BYTES:
        raise ValueError(f"File exceeds {MAX_READ_BYTES} bytes")
    return path.read_text(encoding="utf-8")


def write_file(relative_path: str, content: str) -> str:
    if len(content.encode("utf-8")) > MAX_WRITE_BYTES:
        raise ValueError(f"Content exceeds {MAX_WRITE_BYTES} bytes")

    path = _safe_path(relative_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return str(path.relative_to(WORKSPACE))
