# app/services/assessor_service.py

from __future__ import annotations

from typing import Any, Dict

from app.domain.models import AssessResponse


class AssessorService:
    """
    Thin service layer around the assessor LangGraph.
    """

    def __init__(self, assessor_graph) -> None:
        self._graph = assessor_graph

    def assess(self, patient_id: str, top_k: int = 5) -> AssessResponse:
        if self._graph is None:
            raise RuntimeError("Assessor graph not initialized")

        state: Dict[str, Any] = {"patient_id": patient_id, "top_k": int(top_k)}
        out = self._graph.invoke(state)  # LangGraph returns final state dict
        resp = out.get("response") or {}

        # Ensure response shape matches AssessResponse model
        return AssessResponse(**resp)
