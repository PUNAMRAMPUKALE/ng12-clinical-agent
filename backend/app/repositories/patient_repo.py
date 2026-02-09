from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any, List

from app.domain.models import Patient


@dataclass
class PatientRepository:
    """
    Loads patients from a JSON file and returns Patient objects by patient_id.

    Expected JSON format (list of objects):
    [
      {
        "patient_id": "PT-101",
        "age": 55,
        "symptoms": ["unexplained haemoptysis"],
        "symptom_duration_days": 14,
        "smoking_history": "current smoker",
        "gender": "M"
      },
      ...
    ]
    """

    data_path: str

    def __post_init__(self) -> None:
        self._path = Path(self.data_path)
        self._cache: Dict[str, Patient] = {}
        self._loaded: bool = False

    def _load(self) -> None:
        if self._loaded:
            return

        if not self._path.exists():
            # allow boot even if file missing; repo will return None
            self._loaded = True
            return

        raw = json.loads(self._path.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            raise ValueError("patients json must be a list of objects")

        for row in raw:
            if not isinstance(row, dict):
                continue

            pid = str(row.get("patient_id", "")).strip()
            if not pid:
                continue

            symptoms_val = row.get("symptoms") or []
            if isinstance(symptoms_val, str):
                symptoms: List[str] = [symptoms_val]
            else:
                symptoms = list(symptoms_val)

            self._cache[pid] = Patient(
                patient_id=pid,
                age=int(row.get("age", 0) or 0),
                symptoms=symptoms,
                symptom_duration_days=int(row.get("symptom_duration_days", row.get("duration_days", 0)) or 0),
                smoking_history=str(row.get("smoking_history", "") or "").strip(),
                gender=str(row.get("gender", "") or "").strip(),
                name=str(row.get("name", "") or "").strip() or None,
            )

        self._loaded = True

    def get_patient(self, patient_id: str) -> Optional[Patient]:
        self._load()
        return self._cache.get(str(patient_id).strip())
