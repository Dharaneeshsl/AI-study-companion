from __future__ import annotations

import logging
import os

from groq import Groq

logger = logging.getLogger("groq")

MODEL_NAME = os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile")
DEFAULT_GROQ_BASE_URL = "https://api.groq.com"


def _normalize_groq_base_url(raw_base_url: str) -> str:
    """
    The Groq SDK expects base_url WITHOUT the `/openai/v1` suffix.

    If the user sets `GROQ_BASE_URL=https://api.groq.com/openai/v1`,
    the SDK will otherwise end up calling `/openai/v1/openai/v1/...` (double prefix).
    """
    base = raw_base_url.strip().rstrip("/")
    if base.endswith("/openai/v1"):
        base = base[: -len("/openai/v1")]
    return base or DEFAULT_GROQ_BASE_URL


def call_groq(system_prompt: str, user_message: str) -> str:
    groq_api_key = os.getenv("GROQ_API_KEY", "")
    if not groq_api_key:
        logger.warning("GROQ_API_KEY missing; returning fallback response")
        return "I'm ready to help, but the Groq API key is missing."

    try:
        groq_base_url = _normalize_groq_base_url(
            os.getenv("GROQ_BASE_URL", DEFAULT_GROQ_BASE_URL)
        )
        client = Groq(api_key=groq_api_key, base_url=groq_base_url)
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.5,
        )
        content = response.choices[0].message.content
        return content or "I couldn't generate a response."
    except Exception as exc:
        logger.exception("Groq call failed: %s", exc)
        return "I ran into an error while generating a response."
