from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.domain.models import Patient

class Cache(ABC):
    @abstractmethod
    def get(self, key: str): ...
    @abstractmethod
    def set(self, key: str, value, ttl_s: int): ...

class PatientRepository(ABC):
    @abstractmethod
    def get_patient(self, patient_id: str) -> Optional[Patient]: ...

class EmbeddingProvider(ABC):
    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]: ...

class LLMProvider(ABC):
    @abstractmethod
    def generate_text(self, system: str, user: str) -> str: ...
    @abstractmethod
    def generate_json(self, system: str, user: str, schema_name: str) -> Dict[str, Any]: ...

class VectorStore(ABC):
    @abstractmethod
    def upsert(self, ids: List[str], documents: List[str], metadatas: List[Dict[str, Any]], embeddings: List[List[float]]): ...
    @abstractmethod
    def query(self, query_embedding: List[float], top_k: int) -> List[Dict[str, Any]]: ...

class PolicyEngine(ABC):
    @abstractmethod
    def decide(self, patient: Patient, extracted: Dict[str, Any]) -> Dict[str, Any]: ...

class MemoryStore(ABC):
    @abstractmethod
    def get_history(self, session_id: str) -> List[Dict[str, str]]: ...
    @abstractmethod
    def append(self, session_id: str, role: str, content: str): ...
    @abstractmethod
    def clear(self, session_id: str): ...
