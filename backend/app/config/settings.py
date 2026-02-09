from __future__ import annotations

from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]  # backend/


class Settings(BaseSettings):
    # -------------------------
    # Providers / keys
    # -------------------------
    LLM_PROVIDER: str = Field(default="vertex")  # vertex | openai | etc (your LLMProvider decides)
    LLM_MODEL: str = Field(default="gemini-2.5-flash")
    LLM_TEMPERATURE: float = Field(default=0.0)
    LLM_API_KEY: str | None = Field(default=None)

    EMBEDDING_PROVIDER: str = Field(default="vertex")  # must match NG12Retriever implementation
    EMBEDDING_MODEL: str = Field(default="gemini-embedding-001")

    # Vertex / GCP
    VERTEX_PROJECT: str | None = Field(default=None)
    VERTEX_LOCATION: str = Field(default="us-central1")

    # Back-compat names (optional)
    GCP_PROJECT: str | None = Field(default=None)
    GCP_LOCATION: str = Field(default="us-central1")

    # -------------------------
    # Data paths
    # -------------------------
    PATIENTS_PATH: Path = Field(default=BASE_DIR / "data" / "patients.json")
    PATIENTS_JSON_PATH: Path = Field(default=BASE_DIR / "data" / "patients.json")  # alias for older code
    NG12_PDF_PATH: Path = Field(default=BASE_DIR / "data" / "ng12.pdf")

    # -------------------------
    # Vector store
    # -------------------------
    CHROMA_DIR: Path = Field(default=BASE_DIR / "vector_store" / "chroma")
    CHROMA_COLLECTION: str = Field(default="ng12")

    # -------------------------
    # Retrieval & gating
    # -------------------------
    DEFAULT_TOP_K: int = Field(default=5, ge=1, le=20)
    TOP_K_DEFAULT: int = Field(default=5, ge=1, le=20)  # alias
    MIN_TOP_SCORE: float = Field(default=0.55, ge=0.0, le=1.0)
    MIN_SCORE_GAP: float = Field(default=0.02, ge=0.0, le=1.0)

    # -------------------------
    # Cache TTLs (seconds)
    # -------------------------
    PATIENT_CACHE_TTL_S: int = Field(default=300, ge=30)
    RETRIEVAL_CACHE_TTL_S: int = Field(default=300, ge=30)
    LLM_CACHE_TTL_S: int = Field(default=120, ge=30)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="forbid",
    )


settings = Settings()
