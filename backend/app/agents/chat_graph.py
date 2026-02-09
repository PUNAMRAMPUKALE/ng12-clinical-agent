# app/agents/chat_graph.py

from __future__ import annotations

from typing import TypedDict, List, Dict, Any, Optional

from langgraph.graph import StateGraph, END

from app.domain.models import Citation
from app.validation.citation_verifier import CitationVerifier


CHAT_SYSTEM = """You are an NG12 clinical guidance assistant.
You must answer ONLY using the provided evidence passages.
If the evidence does not support the user's question, say you cannot confirm from NG12 evidence.
When you make any claim, include citations that support it.
If the user asks for treatment/management beyond NG12 referral guidance, say you cannot answer from evidence.
Return JSON with keys:
- answer: string
- supported: boolean
- citations: list of {chunk_id,page,reason}
"""

CHAT_USER_TEMPLATE = """Conversation so far:
{history}

User question:
{message}

Evidence passages:
{evidence}

Return JSON only.
"""


class ChatState(TypedDict, total=False):
    session_id: str
    message: str
    top_k: int

    # memory
    history: List[Dict[str, Any]]  # [{role, content, citations}]
    last_citations: List[Dict[str, Any]]  # citations from previous assistant turn

    # retrieval
    query: str
    evidence_hits: List[Dict[str, Any]]
    retrieval_debug: Dict[str, Any]

    # model output
    model_json: Dict[str, Any]

    # response
    response: Dict[str, Any]


def build_chat_graph(memory_store, retriever, llm):
    verifier = CitationVerifier()

    def _clip(text: str, n: int = 800) -> str:
        s = (text or "").strip()
        return s[:n] + ("..." if len(s) > n else "")

    def _hit_text(h: Dict[str, Any]) -> str:
        return (h.get("document") or h.get("text") or h.get("snippet") or "").strip()

    def load_history(state: ChatState):
        session_id = state["session_id"]
        hist = memory_store.get_history(session_id) or []
        state["history"] = hist

        # capture last assistant citations if present
        last_cits: List[Dict[str, Any]] = []
        for item in reversed(hist):
            if item.get("role") == "assistant":
                last_cits = item.get("citations") or []
                break
        state["last_citations"] = last_cits
        return state

    def build_query(state: ChatState):
        message = (state.get("message") or "").strip()
        hist = state.get("history") or []

        # build a compact history summary for follow-up grounding
        # we keep the last 2 turns max to reduce prompt size
        tail = hist[-4:] if len(hist) > 4 else hist
        hist_lines = []
        for h in tail:
            role = h.get("role", "unknown")
            content = (h.get("content") or "").strip()
            if content:
                hist_lines.append(f"{role.upper()}: {content}")
        history_text = "\n".join(hist_lines)

        # If follow-up, include last assistant answer and citation chunk_ids as anchors
        anchors = []
        for c in (state.get("last_citations") or []):
            cid = (c.get("chunk_id") or "").strip()
            if cid:
                anchors.append(cid)
        anchor_text = ", ".join(anchors[:6])  # keep short

        q = f"ng12 guidance. user_question: {message}."
        if history_text:
            q += f" context: {history_text}."
        if anchor_text:
            q += f" prior_citation_chunks: {anchor_text}."

        state["query"] = q
        return state

    def retrieve(state: ChatState):
        hits, debug = retriever.retrieve(state["query"], top_k=int(state.get("top_k", 5)))
        state["evidence_hits"] = hits or []
        state["retrieval_debug"] = debug or {
            "count": 0,
            "top_score": 0.0,
            "k_score": 0.0,
            "query": state.get("query", ""),
        }
        return state

    def ask_llm(state: ChatState):
        hist = state.get("history") or []
        tail = hist[-6:] if len(hist) > 6 else hist

        # string history for prompt
        lines = []
        for h in tail:
            role = h.get("role", "")
            content = (h.get("content") or "").strip()
            if not content:
                continue
            lines.append(f"{role}: {content}")
        history_text = "\n".join(lines) or "(no prior turns)"

        # include top hits text
        hits = state.get("evidence_hits") or []
        top_hits = hits[:5]

        def fmt_hit(h: Dict[str, Any]) -> str:
            meta = h.get("metadata") or {}
            page = meta.get("page") or h.get("page")
            cid = h.get("id") or h.get("chunk_id") or "unknown"
            txt = _clip(_hit_text(h), 800)
            return f"- chunk_id={cid} page={page}\n  text={txt}"

        evidence_text = "\n\n".join(fmt_hit(h) for h in top_hits) or "(no evidence retrieved)"

        user_prompt = CHAT_USER_TEMPLATE.format(
            history=history_text,
            message=state.get("message", ""),
            evidence=evidence_text,
        )

        out = llm.generate_json(CHAT_SYSTEM, user_prompt, schema_name="chat_answer") or {}
        state["model_json"] = out
        return state

    def validate_and_save(state: ChatState):
        hits = state.get("evidence_hits") or []
        hits_by_id: Dict[str, Dict[str, Any]] = {}

        for h in hits:
            hid = (h.get("id") or h.get("chunk_id") or "").strip()
            if hid:
                hits_by_id[hid] = h

        model_json = state.get("model_json") or {}
        answer = (model_json.get("answer") or "").strip() or "I couldn't find support in retrieved NG12 text."
        supported = bool(model_json.get("supported", False))

        # Build citations strictly from model_json citations_used; fall back to best hit if supported claim exists
        citations: List[Citation] = []
        cited_ids = []

        for c in (model_json.get("citations") or []):
            try:
                cid = str(c.get("chunk_id") or "").strip()
                if not cid:
                    continue
                hit = hits_by_id.get(cid)
                if not hit:
                    continue
                meta = hit.get("metadata") or {}
                page = int(c.get("page") or meta.get("page") or 0)
                excerpt = _clip(_hit_text(hit), 220)
                citations.append(Citation(page=page, chunk_id=cid, excerpt=excerpt))
                cited_ids.append(cid)
            except Exception:
                continue

        # IMPORTANT: If the model says "not supported", still cite the limiting evidence when available.
        # If prior citations exist, reuse them as justification anchors.
        if (not supported) and (not citations):
            for prior in (state.get("last_citations") or []):
                cid = (prior.get("chunk_id") or "").strip()
                if not cid:
                    continue
                # try to cite from current hits first; if missing, just reuse prior citation payload
                hit = hits_by_id.get(cid)
                if hit:
                    meta = hit.get("metadata") or {}
                    page = int(prior.get("page") or meta.get("page") or 0)
                    excerpt = _clip(_hit_text(hit), 220)
                    citations.append(Citation(page=page, chunk_id=cid, excerpt=excerpt))
                else:
                    # reuse prior excerpt if we can't locate it in current hits
                    try:
                        citations.append(
                            Citation(
                                page=int(prior.get("page") or 0),
                                chunk_id=cid,
                                excerpt=_clip(prior.get("excerpt") or "", 220),
                            )
                        )
                    except Exception:
                        pass
                if len(citations) >= 2:
                    break

        # verify citations (best-effort)
        try:
            if citations:
                verifier.verify(citations, hits)
        except Exception:
            pass

        session_id = state["session_id"]

        assistant_turn = {
            "role": "assistant",
            "content": answer,
            "citations": [c.model_dump() for c in citations],
        }
        user_turn = {"role": "user", "content": state.get("message", ""), "citations": []}

        # save turns
        memory_store.append(session_id, user_turn)
        memory_store.append(session_id, assistant_turn)

        state["response"] = {
            "session_id": session_id,
            "answer": answer,
            "citations": [c.model_dump() for c in citations],
        }
        return state

    g = StateGraph(ChatState)
    g.add_node("load_history", load_history)
    g.add_node("build_query", build_query)
    g.add_node("retrieve", retrieve)
    g.add_node("ask_llm", ask_llm)
    g.add_node("validate_and_save", validate_and_save)

    g.set_entry_point("load_history")
    g.add_edge("load_history", "build_query")
    g.add_edge("build_query", "retrieve")
    g.add_edge("retrieve", "ask_llm")
    g.add_edge("ask_llm", "validate_and_save")
    g.add_edge("validate_and_save", END)

    return g.compile()
