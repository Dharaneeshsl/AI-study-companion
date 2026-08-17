from __future__ import annotations

import ast
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict

import httpx

from core.env import load_project_env
from database import database


logger = logging.getLogger("hindsight")
load_project_env()

HINDSIGHT_BASE_URL = os.getenv("HINDSIGHT_BASE_URL", "https://hindsight.vectorize.io")
HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY", "")
HINDSIGHT_PIPELINE_ID = os.getenv("HINDSIGHT_PIPELINE_ID", "")

DEFAULT_MEMORY = (
    "Student weak topics: []\n"
    "Recent mistakes: []\n"
    "Subjects studied: []\n"
    "Learning insights: []\n"
    "Last session: []\n"
    "Upcoming exams: []\n"
    "Study streak: 0 days"
)

_MEMORY_DEFAULTS = {
    "Student weak topics": "[]",
    "Recent mistakes": "[]",
    "Subjects studied": "[]",
    "Learning insights": "[]",
    "Last session": "[]",
    "Upcoming exams": "[]",
    "Study streak": "0 days",
}


MEMORY_DEFAULTS = {
    "Student weak topics": "[]",
    "Recent mistakes": "[]",
    "Subjects studied": "[]",
    "Last session": "[]",
    "Upcoming exams": "[]",
    "Study streak": "0 days",
}


def parse_memory(memory_str: str) -> dict[str, str]:
    parts = {}
    for line in memory_str.strip().split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            parts[key.strip()] = val.strip()

    for key, value in MEMORY_DEFAULTS.items():
        parts.setdefault(key, value)
    return parts


def serialize_memory(memory_dict: dict[str, str]) -> str:
    return (
        f"Student weak topics: {memory_dict.get('Student weak topics', '[]')}\n"
        f"Recent mistakes: {memory_dict.get('Recent mistakes', '[]')}\n"
        f"Subjects studied: {memory_dict.get('Subjects studied', '[]')}\n"
        f"Last session: {memory_dict.get('Last session', '[]')}\n"
        f"Upcoming exams: {memory_dict.get('Upcoming exams', '[]')}\n"
        f"Study streak: {memory_dict.get('Study streak', '0 days')}"
    )


def parse_memory_list(raw: str) -> list[str]:
    try:
        parsed = ast.literal_eval(raw)
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]
    except (SyntaxError, ValueError):
        pass
    return [item.strip() for item in raw.strip("[]").split(",") if item.strip()]


def serialize_memory_list(items: list[str]) -> str:
    cleaned = [item.strip() for item in items if item.strip()]
    return repr(cleaned)


def _auth_headers() -> Dict[str, str]:
    headers: Dict[str, str] = {}
    if HINDSIGHT_API_KEY:
        headers["Authorization"] = f"Bearer {HINDSIGHT_API_KEY}"
    return headers


async def _get_memory_from_hindsight(user_id: str) -> str | None:
    if not HINDSIGHT_BASE_URL:
        return None
    base = HINDSIGHT_BASE_URL.rstrip("/")
    candidates = [
        f"{base}/memory/{user_id}",
        f"{base}/memories/{user_id}",
        f"{base}/api/memory/{user_id}",
        f"{base}/api/memories/{user_id}",
    ]
    params = {"pipeline_id": HINDSIGHT_PIPELINE_ID} if HINDSIGHT_PIPELINE_ID else None
    async with httpx.AsyncClient(timeout=10.0) as client:
        for url in candidates:
            try:
                response = await client.get(url, headers=_auth_headers(), params=params)
                if response.status_code >= 400:
                    continue
                data: Any = response.json()
                if isinstance(data, dict):
                    content = (
                        data.get("content")
                        or data.get("memory")
                        or data.get("text")
                    )
                    if isinstance(content, str) and content.strip():
                        return content
            except Exception:
                logger.debug("Hindsight read failed for %s", url, exc_info=True)
    return None


async def _save_memory_to_hindsight(user_id: str, content: str) -> bool:
    if not HINDSIGHT_BASE_URL:
        return False
    base = HINDSIGHT_BASE_URL.rstrip("/")
    candidates = [
        f"{base}/memory/{user_id}",
        f"{base}/memories/{user_id}",
        f"{base}/api/memory/{user_id}",
        f"{base}/api/memories/{user_id}",
    ]
    headers = {"Content-Type": "application/json", **_auth_headers()}
    payload: Dict[str, Any] = {"content": content}
    if HINDSIGHT_PIPELINE_ID:
        payload["pipeline_id"] = HINDSIGHT_PIPELINE_ID

    async with httpx.AsyncClient(timeout=10.0) as client:
        for url in candidates:
            try:
                response = await client.put(url, headers=headers, json=payload)
                if response.status_code < 400:
                    return True
                response = await client.post(url, headers=headers, json=payload)
                if response.status_code < 400:
                    return True
            except Exception:
                logger.debug("Hindsight write failed for %s", url, exc_info=True)
    return False


async def get_memory(user_id: str) -> str:
    logger.info("Fetching memory for user_id=%s", user_id)
    try:
        remote = await _get_memory_from_hindsight(user_id)
        if remote:
            return remote
        doc = await database.memories.find_one({"user_id": user_id})
        if doc and isinstance(doc.get("content"), str):
            return doc["content"]
        return DEFAULT_MEMORY
    except Exception:
        logger.exception("Failed to fetch memory")
        return DEFAULT_MEMORY


async def save_memory(user_id: str, content: str) -> bool:
    logger.info("Saving memory for user_id=%s", user_id)
    try:
        if await _save_memory_to_hindsight(user_id, content):
            return True
        await database.memories.update_one(
            {"user_id": user_id},
            {"$set": {"content": content}},
            upsert=True,
        )
        return True
    except Exception:
        logger.exception("Failed to save memory")
        return False
