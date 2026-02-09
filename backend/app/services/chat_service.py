# app/services/chat_service.py

from __future__ import annotations

from typing import Any, Dict

from app.domain.models import ChatResponse, ChatHistoryResponse, ChatTurn


class ChatService:
    """
    Service layer for chat graph + memory.
    """

    def __init__(self, chat_graph, memory_store) -> None:
        self._graph = chat_graph
        self._memory = memory_store

    def chat(self, session_id: str, message: str, top_k: int = 5) -> ChatResponse:
        if self._graph is None:
            raise RuntimeError("Chat graph not initialized")

        state: Dict[str, Any] = {
            "session_id": session_id,
            "message": message,
            "top_k": int(top_k),
        }

        out = self._graph.invoke(state)
        resp = out.get("response") or {}

        return ChatResponse(**resp)

    def history(self, session_id: str) -> ChatHistoryResponse:
        hist = self._memory.get_history(session_id) or []
        turns = []
        for h in hist:
            turns.append(
                ChatTurn(
                    role=h.get("role", "user"),
                    content=h.get("content", ""),
                    citations=h.get("citations") or [],
                )
            )
        return ChatHistoryResponse(session_id=session_id, history=turns)

    def clear(self, session_id: str) -> Dict[str, Any]:
        self._memory.clear(session_id)
        return {"session_id": session_id, "cleared": True}
