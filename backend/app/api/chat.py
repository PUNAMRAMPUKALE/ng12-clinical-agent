from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.config.container import Container
from app.api.deps import get_container
from app.domain.models import ChatRequest, ChatResponse, ChatHistoryResponse

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, c: Container = Depends(get_container)):
    try:
        return c.chat_service.chat(req.session_id, req.message, req.top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/{session_id}/history", response_model=ChatHistoryResponse)
def history(session_id: str, c: Container = Depends(get_container)):
    try:
        return c.chat_service.history(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/chat/{session_id}")
def clear(session_id: str, c: Container = Depends(get_container)):
    try:
        return c.chat_service.clear(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
