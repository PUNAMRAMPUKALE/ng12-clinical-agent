# scripts/ingest_ng12.py

import os
import re
from typing import List, Dict, Any

from pypdf import PdfReader

from app.config.settings import settings
from app.stores.chroma_store import ChromaVectorStore
from app.providers.vertex_embeddings import VertexEmbeddingProvider


FOOTER_PATTERNS = [
    r"^page\s+\d+\s+of\s+\d+.*$",
    r"^©\s*nice.*$",
    r"^www\.nice\.org\.uk.*$",
    r"^subject to notice of rights.*$",
    r"^terms-and-conditions.*$",
]


def _looks_like_footer_or_header(line: str) -> bool:
    low = (line or "").strip().lower()
    if not low:
        return True
    for pat in FOOTER_PATTERNS:
        if re.match(pat, low):
            return True
    if "all rights reserved" in low:
        return True
    if "notice of rights" in low:
        return True
    return False


def clean_text(t: str) -> str:
    """
    Keep clinically meaningful lines; remove obvious noise.
    """
    t = (t or "").replace("\u00a0", " ")
    lines: List[str] = []
    for ln in t.splitlines():
        s = (ln or "").strip()
        if not s:
            continue
        if _looks_like_footer_or_header(s):
            continue
        # reduce repeated whitespace
        s = re.sub(r"\s+", " ", s).strip()
        if s:
            lines.append(s)
    return "\n".join(lines)


def split_into_paragraph_chunks(text: str, max_chars: int = 1400, overlap_chars: int = 160) -> List[str]:
    """
    Better than raw fixed slicing:
    - split by paragraphs
    - pack paragraphs into chunks
    - add small overlap for continuity
    """
    paras = [p.strip() for p in (text or "").split("\n") if p.strip()]
    chunks: List[str] = []
    cur = ""

    for p in paras:
        if not cur:
            cur = p
            continue

        if len(cur) + 1 + len(p) <= max_chars:
            cur = cur + "\n" + p
        else:
            chunks.append(cur.strip())
            # overlap: take tail of previous
            tail = cur[-overlap_chars:] if overlap_chars > 0 else ""
            cur = (tail + "\n" + p).strip()

    if cur.strip():
        chunks.append(cur.strip())

    return chunks


def has_criteria_signals(text: str) -> bool:
    t = (text or "").lower()
    signals = [
        "refer", "consider", "offer", "suspected cancer pathway",
        "symptom and specific features", "possible cancer", "recommendation",
        "aged", "and over", "within", "weeks",
    ]
    return any(s in t for s in signals)


def main():
    pdf_path = str(settings.NG12_PDF_PATH)
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"NG12 PDF not found at {pdf_path}")

    reader = PdfReader(pdf_path)
    store = ChromaVectorStore()
    embedder = VertexEmbeddingProvider()

    ids: List[str] = []
    docs: List[str] = []
    metas: List[Dict[str, Any]] = []

    for page_idx, page in enumerate(reader.pages, start=1):
        raw = page.extract_text() or ""
        text = clean_text(raw)
        if not text:
            continue

        chunks = split_into_paragraph_chunks(text, max_chars=1400, overlap_chars=160)
        for ci, ch in enumerate(chunks):
            ch = ch.strip()
            if not ch:
                continue

            chunk_id = f"ng12_{page_idx:04d}_{ci:02d}"
            ids.append(chunk_id)
            docs.append(ch)
            metas.append(
                {
                    "page": page_idx,
                    "source": "NG12 PDF",
                    "has_criteria": bool(has_criteria_signals(ch)),
                }
            )

    # batch embed + upsert
    B = 32
    for start in range(0, len(docs), B):
        batch_docs = docs[start : start + B]
        batch_ids = ids[start : start + B]
        batch_metas = metas[start : start + B]
        embs = embedder.embed_texts(batch_docs)
        store.upsert(batch_ids, batch_docs, batch_metas, embs)

    print(f"Indexed {len(ids)} chunks into {settings.CHROMA_DIR} / {settings.CHROMA_COLLECTION}")


if __name__ == "__main__":
    main()
