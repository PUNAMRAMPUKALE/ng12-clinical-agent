from __future__ import annotations

from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel, Field


class Patient(BaseModel):
    patient_id: str
    name: Optional[str] = None
    age: int
    gender: str = ""                 # default so your JSON can omit it
    smoking_history: str = ""        # default so your JSON can omit it
    symptoms: List[str] = Field(default_factory=list)
    symptom_duration_days: int = 0   # default


class Citation(BaseModel):
    source: str = "NG12 PDF"
    page: int
    chunk_id: str
    excerpt: str = ""


class AssessRequest(BaseModel):
    patient_id: str
    top_k: int = 5


class AssessResponse(BaseModel):
    patient_id: str
    assessment: str
    reasoning: str
    citations: List[Citation] = Field(default_factory=list)
    confidence: Optional[float] = None
    retrieval_debug: Dict[str, Any] = Field(default_factory=dict)


class ChatRequest(BaseModel):
    session_id: str
    message: str
    top_k: int = 5


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    citations: List[Citation] = Field(default_factory=list)


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    citations: List[Citation] = Field(default_factory=list)


class ChatHistoryResponse(BaseModel):
    session_id: str
    history: List[ChatTurn] = Field(default_factory=list)


Patient.model_rebuild()
Citation.model_rebuild()
AssessRequest.model_rebuild()
AssessResponse.model_rebuild()
ChatRequest.model_rebuild()
ChatResponse.model_rebuild()
ChatTurn.model_rebuild()
ChatHistoryResponse.model_rebuild()
