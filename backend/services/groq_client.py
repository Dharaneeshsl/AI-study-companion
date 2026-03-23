from __future__ import annotations

import logging
import os
from typing import Optional

from groq import Groq

logger = logging.getLogger("groq")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
MODEL_NAME = "llama-3.3-70b-versatile"


def call_groq(system_prompt: str, user_message: str) -> str:
    if not GROQ_API_KEY:
        logger.warning("GROQ_API_KEY missing; returning fallback response")
        return "I'm ready to help, but the Groq API key is missing."

    try:
        client = Groq(api_key=GROQ_API_KEY)
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
