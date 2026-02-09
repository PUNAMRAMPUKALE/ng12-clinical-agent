from __future__ import annotations

from fastapi import Request
from app.config.container import Container


def get_container(request: Request) -> Container:
    c = getattr(request.app.state, "container", None)
    if c is None:
        raise RuntimeError("Container not initialized on app.state.container")
    return c
