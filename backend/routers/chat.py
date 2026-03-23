from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Tuple

from fastapi import APIRouter, HTTPException

from models.chat import ChatRequest, ChatResponse
from services.groq_client import call_groq
from services.hindsight import get_memory, save_memory, parse_memory, serialize_memory

logger = logging.getLogger("router.chat")

router = APIRouter(prefix="/api", tags=["chat"])


def _build_system_prompt(memory: str) -> str:
    return (
        "You are an AI study companion. Personalize every response based on the student's memory.\n"
        "Always reference the memory explicitly: highlight weak topics, recent mistakes, study streak, "
        "and any upcoming exams. Tailor tone and pacing to the student's history.\n"
        "If the user asks a new question, connect it to their weak topics or prior mistakes when possible.\n"
        "Return your response in this exact format:\n"
        "REPLY:\n<assistant reply>\n\n"
        "INSIGHT:\n<one or two sentences summarizing learning insight to store in memory>\n\n"
        "MEMORY CONTEXT:\n"
        f"{memory}\n"
    )


def _parse_reply(content: str) -> Tuple[str, str]:
    if "REPLY:" in content and "INSIGHT:" in content:
        reply_part = content.split("REPLY:", 1)[1]
        reply_text, insight_part = reply_part.split("INSIGHT:", 1)
        return reply_text.strip(), insight_part.strip()
    return content.strip(), "Student engaged in chat; update topics discussed."


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        memory = await get_memory(request.user_id)
        system_prompt = _build_system_prompt(memory)
        logger.info("Calling Groq for chat user_id=%s", request.user_id)
        raw = call_groq(system_prompt, request.message)
        reply, insight = _parse_reply(raw)

        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        
        mem_dict = parse_memory(memory)
        mem_dict["Last session"] = timestamp
        
        current_topics = mem_dict["Student weak topics"].strip("[]").replace("'", "").replace('"', '').split(",")
        current_topics.append(insight)
        cleaned_topics = [t.strip() for t in current_topics if t.strip()]
        if len(cleaned_topics) > 3:
            cleaned_topics = cleaned_topics[-3:]
        mem_dict["Student weak topics"] = "[" + ", ".join(cleaned_topics) + "]"
        
        updated_memory = serialize_memory(mem_dict)
        await save_memory(request.user_id, updated_memory)
        return ChatResponse(reply=reply)
    except Exception as exc:
        logger.exception("Chat endpoint failed: %s", exc)
        raise HTTPException(status_code=500, detail="Chat failed")
