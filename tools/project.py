from pathlib import Path
from .files import WORKSPACE, list_files


def project_status() -> dict:
    files = list_files(".")
    return {
        "workspace": str(WORKSPACE),
        "file_count": len(files),
        "files": files,
    }
