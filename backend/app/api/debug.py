from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.config.container import Container
from app.api.deps import get_container

router = APIRouter(prefix="/debug", tags=["debug"])


class DebugQueryRequest(BaseModel):
    query: str
    top_k: int = 5


@router.post("/retrieve")
def debug_retrieve(req: DebugQueryRequest, c: Container = Depends(get_container)):
    hits, debug = c.retriever.retrieve(req.query, req.top_k)

    trimmed: List[Dict[str, Any]] = []
    for h in hits[: req.top_k]:
        meta = h.get("metadata") or {}
        trimmed.append(
            {
                "id": h.get("id"),
                "page": meta.get("page") or h.get("page"),
                "score": h.get("score"),
                "distance": h.get("distance"),
                "snippet": (h.get("document") or h.get("text") or h.get("snippet") or "")[:250],
            }
        )

    return {"debug": debug, "hits": trimmed}
