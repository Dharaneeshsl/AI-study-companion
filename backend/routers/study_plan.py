from __future__ import annotations

import json
import logging
import re
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from core.security import get_current_user
from models.study_plan import StudyPlanRequest, StudyPlanResponse, StudyDay, StudySession
from services.groq_client import call_groq
from services.hindsight import get_memory

logger = logging.getLogger("router.study_plan")

router = APIRouter(prefix="/api", tags=["study-plan"])


def _build_plan_prompt(memory: str) -> str:
    return (
        "You are an AI study coach. Use the student's memory to build a weekly study plan.\n"
        "Incorporate weak topics, recent mistakes, upcoming exams, and study streak into "
        "the schedule.\n"
        "Balance difficulty and recovery; include at least one lighter review day if "
        "streak is low.\n"
        "Return ONLY valid JSON in this format:\n"
        "{\"plan\": [\n"
        "  {\"day\": \"Monday\", \"sessions\": ["
        "{\"subject\": \"Maths\", \"time\": \"6:00-7:00 PM\", \"focus\": \"Algebra drills\"}"
        "]}\n"
        "]}\n\n"
        "MEMORY CONTEXT:\n"
        f"{memory}\n"
    )


def _extract_json(text: str) -> dict:
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No JSON found")
    return json.loads(match.group(0))


def _fallback_plan() -> List[StudyDay]:
    return [
        StudyDay(
            day="Monday",
            sessions=[
                StudySession(
                    subject="Maths",
                    time="6:00-7:00 PM",
                    focus="Core practice",
                ),
                StudySession(
                    subject="Physics",
                    time="7:30-8:00 PM",
                    focus="Quick review",
                ),
            ],
        ),
        StudyDay(
            day="Tuesday",
            sessions=[
                StudySession(
                    subject="Chemistry",
                    time="6:00-7:00 PM",
                    focus="Concept review",
                ),
                StudySession(
                    subject="English",
                    time="7:30-8:00 PM",
                    focus="Reading practice",
                ),
            ],
        ),
        StudyDay(
            day="Wednesday",
            sessions=[
                StudySession(
                    subject="CS",
                    time="6:00-7:00 PM",
                    focus="Problem solving",
                ),
                StudySession(
                    subject="Maths",
                    time="7:30-8:00 PM",
                    focus="Mistake review",
                ),
            ],
        ),
        StudyDay(
            day="Thursday",
            sessions=[
                StudySession(
                    subject="Physics",
                    time="6:00-7:00 PM",
                    focus="Numericals",
                ),
                StudySession(
                    subject="Chemistry",
                    time="7:30-8:00 PM",
                    focus="Flashcards",
                ),
            ],
        ),
        StudyDay(
            day="Friday",
            sessions=[
                StudySession(
                    subject="CS",
                    time="6:00-7:00 PM",
                    focus="Implementation drills",
                ),
                StudySession(
                    subject="Maths",
                    time="7:30-8:00 PM",
                    focus="Timed practice",
                ),
            ],
        ),
        StudyDay(
            day="Saturday",
            sessions=[
                StudySession(
                    subject="Mixed",
                    time="10:00-11:00 AM",
                    focus="Weekly mock quiz",
                ),
                StudySession(
                    subject="Review",
                    time="5:00-5:30 PM",
                    focus="Error log cleanup",
                ),
            ],
        ),
        StudyDay(
            day="Sunday",
            sessions=[
                StudySession(
                    subject="Review",
                    time="5:00-6:00 PM",
                    focus="Light revision",
                ),
            ],
        ),
    ]


@router.post("/study-plan", response_model=StudyPlanResponse)
async def generate_plan(
    request: StudyPlanRequest,
    current_user=Depends(get_current_user),
) -> StudyPlanResponse:
    try:
        user_id = current_user["user_id"]
        memory = await get_memory(user_id)
        system_prompt = _build_plan_prompt(memory)
        logger.info("Calling Groq for study plan user_id=%s", user_id)
        raw = call_groq(system_prompt, "Create a weekly study plan.")
        try:
            data = _extract_json(raw)
            plan_raw = data.get("plan", [])
            plan = [StudyDay(**day) for day in plan_raw]
            if not plan:
                raise ValueError("Empty plan")
        except Exception:
            logger.warning("Failed to parse plan JSON; using fallback")
            plan = _fallback_plan()
        return StudyPlanResponse(plan=plan)
    except Exception as exc:
        logger.exception("Study plan generation failed: %s", exc)
        raise HTTPException(status_code=500, detail="Study plan generation failed")
