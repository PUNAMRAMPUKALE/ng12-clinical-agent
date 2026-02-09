# app/utils/text.py

import hashlib


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_query(q: str) -> str:
    q = (q or "").lower().strip()

    # UK spellings typical in NG12
    q = q.replace("hemoptysis", "haemoptysis")
    q = q.replace("anemia", "anaemia")

    # Disambiguation: dysphagia vs dyspepsia
    # "dysphagia" means difficulty swallowing; add anchor phrase to improve retrieval.
    if "dysphagia" in q:
        q = q.replace("dysphagia", "dysphagia (difficulty swallowing)")

    return q
