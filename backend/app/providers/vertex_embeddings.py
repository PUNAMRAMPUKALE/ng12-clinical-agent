from __future__ import annotations

from typing import List
import os

from app.config.settings import settings


class VertexEmbeddingProvider:
    """
    Embeddings provider used by:
      - scripts/ingest_ng12.py
      - app/retrieval/ng12_retriever.py

    Implementation:
      - Uses Vertex AI Text Embeddings model (via google-cloud-aiplatform).
      - Requires GOOGLE_APPLICATION_CREDENTIALS env var set (service account json)
        OR `gcloud auth application-default login`.
    """

    def __init__(self, model_name: str | None = None, project: str | None = None, location: str | None = None):
        self.model_name = model_name or getattr(settings, "EMBEDDING_MODEL", "text-embedding-004")
        self.project = project or getattr(settings, "GCP_PROJECT", None) or getattr(settings, "GCP_PROJECT_ID", None)
        self.location = location or getattr(settings, "GCP_LOCATION", "us-central1")

        if not self.project:
            # settings is strict; but keeping this error explicit
            raise RuntimeError("GCP project not set. Please set GCP_PROJECT in .env")

        # Lazy init so import doesn't crash if deps missing until used
        self._inited = False
        self._model = None

    def _init(self) -> None:
        if self._inited:
            return

        try:
            import vertexai
            from vertexai.preview.language_models import TextEmbeddingModel
        except Exception as e:
            raise RuntimeError(
                "Missing Vertex AI dependencies. Install:\n"
                "  pip install google-cloud-aiplatform vertexai\n"
                f"Original error: {e}"
            )

        vertexai.init(project=self.project, location=self.location)
        self._model = TextEmbeddingModel.from_pretrained(self.model_name)
        self._inited = True

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        self._init()

        clean = []
        for t in texts or []:
            s = (t or "").strip()
            if not s:
                s = " "  # Vertex doesn't like empty strings
            clean.append(s)

        # Vertex returns objects with .values for embedding vector
        res = self._model.get_embeddings(clean)
        out: List[List[float]] = []
        for r in res:
            # r.values is a list[float]
            out.append(list(r.values))
        return out
