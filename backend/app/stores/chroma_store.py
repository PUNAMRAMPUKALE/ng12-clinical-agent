from __future__ import annotations

from typing import List, Dict, Any, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.domain.interfaces import VectorStore


class ChromaVectorStore(VectorStore):
    """
    Thin wrapper over Chroma persistent collection.

    Expected hit shape for your app:
      {
        "id": str,
        "document": str,
        "metadata": dict,
        "distance": float,
        "score": float  # derived, higher = better
      }
    """

    def __init__(self, persist_dir: Optional[str] = None, collection_name: Optional[str] = None):
        # Lazy import to avoid circular settings imports
        from app.config.settings import settings

        pdir = persist_dir or str(settings.CHROMA_DIR)
        cname = collection_name or str(settings.CHROMA_COLLECTION)

        self._client = chromadb.PersistentClient(
            path=str(pdir),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._col = self._client.get_or_create_collection(name=str(cname))

    def upsert(
        self,
        ids: List[str],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        embeddings: List[List[float]],
    ):
        self._col.upsert(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)

    def query(self, query_embedding: List[float], top_k: int) -> List[Dict[str, Any]]:
        res = self._col.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        hits: List[Dict[str, Any]] = []
        ids0 = res.get("ids", [[]])[0]
        docs0 = res.get("documents", [[]])[0]
        metas0 = res.get("metadatas", [[]])[0]
        dists0 = res.get("distances", [[]])[0]

        for i in range(len(ids0)):
            dist = float(dists0[i]) if dists0 and i < len(dists0) else 0.0
            # Convert distance -> score (higher is better). Simple invert.
            score = max(0.0, 1.0 - dist)

            hits.append(
                {
                    "id": ids0[i],
                    "document": docs0[i] if i < len(docs0) else "",
                    "metadata": metas0[i] if i < len(metas0) else {},
                    "distance": dist,
                    "score": score,
                }
            )

        return hits
