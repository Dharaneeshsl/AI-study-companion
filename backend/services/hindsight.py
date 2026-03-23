from __future__ import annotations

import logging
import os
from typing import Optional

import httpx

logger = logging.getLogger("hindsight")

HINDSIGHT_BASE_URL = os.getenv("HINDSIGHT_BASE_URL", "https://hindsight.vectorize.io")
HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY", "")
HINDSIGHT_PIPELINE_ID = os.getenv("HINDSIGHT_PIPELINE_ID", "")

DEFAULT_MEMORY = (
    "Student weak topics: []\n"
    "Recent mistakes: []\n"
    "Subjects studied: []\n"
    "Last session: []\n"
    "Upcoming exams: []\n"
    "Study streak: 0 days"
)


def parse_memory(memory_str: str) -> dict:
    parts = {}
    for line in memory_str.strip().split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            parts[key.strip()] = val.strip()
    
    defaults = {
        "Student weak topics": "[]",
        "Recent mistakes": "[]",
        "Subjects studied": "[]",
        "Last session": "[]",
        "Upcoming exams": "[]",
        "Study streak": "0 days"
    }
    for k, v in defaults.items():
        if k not in parts:
            parts[k] = v
    return parts


def serialize_memory(memory_dict: dict) -> str:
    return (
        f"Student weak topics: {memory_dict.get('Student weak topics', '[]')}\n"
        f"Recent mistakes: {memory_dict.get('Recent mistakes', '[]')}\n"
        f"Subjects studied: {memory_dict.get('Subjects studied', '[]')}\n"
        f"Last session: {memory_dict.get('Last session', '[]')}\n"
        f"Upcoming exams: {memory_dict.get('Upcoming exams', '[]')}\n"
        f"Study streak: {memory_dict.get('Study streak', '0 days')}"
    )


def _headers() -> dict[str, str]:
    if not HINDSIGHT_API_KEY:
        return {}
    return {"Authorization": f"Bearer {HINDSIGHT_API_KEY}"}


def _memory_url(user_id: str) -> str:
    return f"{HINDSIGHT_BASE_URL}/api/v1/memory/{HINDSIGHT_PIPELINE_ID}/{user_id}"


async def get_memory(user_id: str) -> str:
    if not HINDSIGHT_API_KEY or not HINDSIGHT_PIPELINE_ID:
        logger.warning("Hindsight credentials missing; returning default memory")
        return DEFAULT_MEMORY

    url = _memory_url(user_id)
    logger.info("Fetching memory for user_id=%s", user_id)
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(url, headers=_headers())
            if response.status_code == 404:
                logger.info("No memory found; returning default")
                return DEFAULT_MEMORY
            response.raise_for_status()
            data = response.json()
            content = data.get("content") if isinstance(data, dict) else None
            return content or DEFAULT_MEMORY
    except httpx.HTTPError as exc:
        logger.exception("Failed to fetch memory: %s", exc)
        return DEFAULT_MEMORY


async def save_memory(user_id: str, content: str) -> bool:
    if not HINDSIGHT_API_KEY or not HINDSIGHT_PIPELINE_ID:
        logger.warning("Hindsight credentials missing; skipping save")
        return False

    url = _memory_url(user_id)
    payload = {"content": content}
    logger.info("Saving memory for user_id=%s", user_id)
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.put(url, json=payload, headers=_headers())
            response.raise_for_status()
            return True
    except httpx.HTTPError as exc:
        logger.exception("Failed to save memory: %s", exc)
        return False
