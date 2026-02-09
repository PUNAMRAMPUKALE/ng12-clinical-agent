# app/policy/assessment_policy.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from app.domain.models import Patient


@dataclass
class AssessmentPolicy:
    """
    Policy engine that converts extracted NG12 criteria into a final assessment.

    Inputs:
      - patient: Patient
      - extracted: dict produced by assessor_graph LLM extraction step

    Output shape:
      {
        "assessment": "Urgent Referral" | "Unclear",
        "confidence": float
      }
    """

    min_top_score: float = 0.55

    def decide(self, patient: Patient, extracted: Dict[str, Any]) -> Dict[str, Any]:
        # If the extractor explicitly says evidence is insufficient, we stay conservative
        if extracted.get("insufficient_evidence") is True:
            return {"assessment": "Unclear", "confidence": 0.20}

        matched = extracted.get("matched_rules") or []
        if not isinstance(matched, list) or len(matched) == 0:
            return {"assessment": "Unclear", "confidence": 0.20}

        # If we matched at least one referral/investigation rule, we mark urgent referral.
        # The assessor_graph already gates evidence quality using retrieval_debug.
        return {"assessment": "Urgent Referral", "confidence": 0.75}
