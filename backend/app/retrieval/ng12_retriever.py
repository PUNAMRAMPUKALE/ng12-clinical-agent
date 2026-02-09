from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Optional

from app.utils.text import normalize_query
from app.stores.chroma_store import ChromaVectorStore
from app.providers.vertex_embeddings import VertexEmbeddingProvider


@dataclass
class NG12Retriever:
    """
    Retrieves top-k chunks from Chroma for a query.

    Returns:
      hits: [{id, document, metadata, distance, score}]
      debug: {count, top_score, k_score, query}
    """
    store: ChromaVectorStore
    embedding_provider: str = "vertex"  # kept for compatibility with Container
    top_k_default: int = 5

    def __post_init__(self) -> None:
        # For now we only support Vertex embedding provider as your ingest script uses it.
        # If you later add another provider, branch here.
        self._embedder = VertexEmbeddingProvider()

    @staticmethod
    def _distance_to_score(distance: float) -> float:
        """
        Chroma returns distance. Depending on metric, lower distance is better.
        Convert to a [0,1] style score where higher is better.
        This is a monotonic transform: score = 1 / (1 + distance)
        """
        try:
            d = float(distance)
        except Exception:
            d = 999999.0
        return 1.0 / (1.0 + max(0.0, d))

    def retrieve(self, query: str, top_k: Optional[int] = None) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        k = int(top_k or self.top_k_default or 5)
        q = normalize_query(query or "")

        if not q.strip():
            return [], {"count": 0, "top_score": 0.0, "k_score": 0.0, "query": q}

        # Embed query
        q_embs = self._embedder.embed_texts([q])
        if not q_embs or not q_embs[0]:
            return [], {"count": 0, "top_score": 0.0, "k_score": 0.0, "query": q}

        # Query store
        hits = self.store.query(query_embedding=q_embs[0], top_k=k) or []

        # Add score field (derived from distance) for downstream logic
        for h in hits:
            dist = h.get("distance", 999999.0)
            h["score"] = self._distance_to_score(dist)

        top_score = float(hits[0]["score"]) if hits else 0.0
        k_score = float(hits[-1]["score"]) if hits else 0.0

        debug = {
            "count": len(hits),
            "top_score": top_score,
            "k_score": k_score,
            "query": q,
        }
        return hits, debug
