# app/providers/llm_provider.py

from __future__ import annotations

import json
from typing import Any, Dict, Optional

from app.config.settings import settings

# If you already have vertex_llm.py in _trash_unused or elsewhere, we can reuse it.
# For now, this provider is a thin wrapper that supports:
# - generate_text(system, user)
# - generate_json(system, user, schema_name)
#
# You can later swap implementation without touching graphs.


class LLMProvider:
    """
    Simple LLM wrapper used by LangGraph nodes.
    Expected interface:
      - generate_text(system: str, user: str) -> str
      - generate_json(system: str, user: str, schema_name: str) -> Dict[str, Any]
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.0,
        api_key: Optional[str] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
    ) -> None:
        self.provider = (provider or "vertex").lower()
        self.model = model or settings.LLM_MODEL
        self.temperature = float(temperature)

        # Vertex settings
        self.project = project or getattr(settings, "GCP_PROJECT", None) or getattr(settings, "GCP_PROJECT_ID", None) or getattr(settings, "GCP_PROJECT", None)
        self.location = location or getattr(settings, "GCP_LOCATION", "us-central1")

        # Lazy init client to avoid import errors if not used in some environments
        self._client = None

    # -----------------------------
    # Internal: Vertex client
    # -----------------------------
    def _get_vertex_client(self):
        if self._client is not None:
            return self._client

        # NOTE:
        # The simplest stable approach is using google-generativeai OR vertexai preview chat.
        # Since your environment may already have one installed, we try vertexai first.
        try:
            import vertexai
            from vertexai.generative_models import GenerativeModel

            vertexai.init(project=self.project, location=self.location)
            self._client = GenerativeModel(self.model)
            self._client_kind = "vertexai"
            return self._client
        except Exception:
            pass

        # Fallback: google-generativeai (Gemini API)
        try:
            import google.generativeai as genai

            # If you use Gemini API key, set GOOGLE_API_KEY or similar
            api_key = getattr(settings, "LLM_API_KEY", None) or getattr(settings, "GOOGLE_API_KEY", None)
            if not api_key:
                raise RuntimeError("Missing GOOGLE_API_KEY / LLM_API_KEY for google.generativeai fallback")

            genai.configure(api_key=api_key)
            self._client = genai.GenerativeModel(self.model)
            self._client_kind = "genai"
            return self._client
        except Exception as e:
            raise RuntimeError(
                "No supported LLM client available. Install vertexai or google-generativeai, and set project/location or API key."
            ) from e

    # -----------------------------
    # Public API
    # -----------------------------
    def generate_text(self, system: str, user: str) -> str:
        client = self._get_vertex_client()

        prompt = (system or "").strip() + "\n\n" + (user or "").strip()

        if getattr(self, "_client_kind", "") == "vertexai":
            resp = client.generate_content(prompt)
            return (getattr(resp, "text", None) or "").strip()

        # genai
        resp = client.generate_content(prompt)
        return (getattr(resp, "text", None) or "").strip()

    def generate_json(self, system: str, user: str, schema_name: str) -> Dict[str, Any]:
        """
        We ask the model to return JSON only, then parse.
        If parsing fails, return {} (graphs already handle empty output safely).
        """
        json_guard = (
            "\n\nReturn ONLY valid JSON. No markdown. No extra keys. No trailing comments.\n"
        )
        text = self.generate_text(system + json_guard, user)

        # Strip common wrappers
        t = (text or "").strip()
        if t.startswith("```"):
            t = t.strip("`")
            # remove optional 'json' language tag
            t = t.replace("json\n", "", 1).strip()

        try:
            return json.loads(t)
        except Exception:
            return {}
