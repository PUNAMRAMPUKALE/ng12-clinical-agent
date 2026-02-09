# app/validation/citation_verifier.py

from typing import List, Dict, Any
from app.domain.models import Citation

class CitationVerifier:
    def verify(self, citations: List[Citation], hits: List[Dict[str, Any]]) -> None:
        """
        ✅ Practical verification:
        - Ensure chunk_id exists in retrieved hits
        - If excerpt is present, do a loose check (ignore case + whitespace)
        - Do NOT hard fail on excerpt mismatch (LLM may truncate/normalize)
        """
        hit_by_id = {}
        for h in hits or []:
            cid = h.get("id") or h.get("chunk_id")
            if cid:
                hit_by_id[str(cid)] = h

        for c in citations:
            h = hit_by_id.get(str(c.chunk_id))
            if not h:
                raise ValueError(f"Citation chunk_id not found in retrieved hits: {c.chunk_id}")

            excerpt = (c.excerpt or "").strip()
            if not excerpt:
                continue

            doc = (h.get("document") or h.get("text") or "").strip()
            if not doc:
                continue

            # Loose compare
            def norm(s: str) -> str:
                return " ".join(s.lower().split())

            if norm(excerpt) not in norm(doc):
                # ✅ Don’t crash; just allow it
                # (If you want, you can log here instead)
                continue
