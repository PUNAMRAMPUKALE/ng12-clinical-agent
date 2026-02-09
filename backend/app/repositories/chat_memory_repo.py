from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class InMemoryChatRepository:
    """
    Simple in-memory chat memory:
    history[session_id] = [
      {"role":"user","content":"...","citations":[]},
      {"role":"assistant","content":"...","citations":[...]}
    ]
    """

    _history: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)

    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        return list(self._history.get(session_id, []))

    def append(self, session_id: str, item: Dict[str, Any]) -> None:
        if session_id not in self._history:
            self._history[session_id] = []
        self._history[session_id].append(item)

    def clear(self, session_id: str) -> Dict[str, Any]:
        self._history[session_id] = []
        return {"session_id": session_id, "cleared": True}
