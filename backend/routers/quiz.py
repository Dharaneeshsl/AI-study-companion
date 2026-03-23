from __future__ import annotations

import json
import logging
import re
from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException

from models.quiz import (
    QuizRequest,
    QuizResponse,
    QuizSubmitRequest,
    QuizResult,
    QuizFeedback,
    QuizQuestion,
)
from services.groq_client import call_groq
from services.hindsight import get_memory, save_memory, parse_memory, serialize_memory

logger = logging.getLogger("router.quiz")

router = APIRouter(prefix="/api/quiz", tags=["quiz"])


def _build_quiz_prompt(memory: str, subject: str) -> str:
    return (
        "You are an AI tutor creating a personalized quiz.\n"
        "Use the student's memory to target weak topics in the given subject.\n"
        "Prioritize topics explicitly mentioned as weak or recently mistaken.\n"
        "Return ONLY valid JSON in this format:\n"
        "{\"questions\": [\n"
        "  {\"id\": \"q1\", \"question\": \"...\", \"options\": [\"A\", \"B\", \"C\", \"D\"], "
        "\"answer\": \"A\", \"explanation\": \"...\", \"topic\": \"...\"}\n"
        "]}\n\n"
        f"Subject: {subject}\n"
        "MEMORY CONTEXT:\n"
        f"{memory}\n"
    )


def _extract_json(text: str) -> dict:
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No JSON found")
    return json.loads(match.group(0))


def _fallback_questions(subject: str) -> List[QuizQuestion]:
    return [
        QuizQuestion(
            id=f"q{i}",
            question=f"Sample {subject} question {i}",
            options=["A", "B", "C", "D"],
            answer="A",
            explanation="Default fallback explanation.",
            topic="Basics",
        )
        for i in range(1, 6)
    ]


@router.post("/generate", response_model=QuizResponse)
async def generate_quiz(request: QuizRequest) -> QuizResponse:
    try:
        memory = await get_memory(request.user_id)
        system_prompt = _build_quiz_prompt(memory, request.subject)
        logger.info("Calling Groq for quiz generation user_id=%s", request.user_id)
        raw = call_groq(system_prompt, "Generate 5 personalized questions.")
        try:
            data = _extract_json(raw)
            questions_raw = data.get("questions", [])
            questions = [QuizQuestion(**q) for q in questions_raw]
            if len(questions) != 5:
                raise ValueError("Expected 5 questions")
        except Exception:
            logger.warning("Failed to parse quiz JSON; using fallback")
            questions = _fallback_questions(request.subject)
        return QuizResponse(questions=questions)
    except Exception as exc:
        logger.exception("Quiz generation failed: %s", exc)
        raise HTTPException(status_code=500, detail="Quiz generation failed")


@router.post("/submit", response_model=QuizResult)
async def submit_quiz(request: QuizSubmitRequest) -> QuizResult:
    try:
        total = len(request.answers)
        feedback: List[QuizFeedback] = []
        score = 0
        mistakes = []

        for answer in request.answers:
            is_correct = answer.selected.strip() == answer.correct.strip()
            if is_correct:
                score += 1
            else:
                mistakes.append(
                    f"{request.subject} - {answer.topic}: missed '{answer.question}'"
                )
            feedback.append(
                QuizFeedback(
                    id=answer.id,
                    correct=is_correct,
                    selected=answer.selected,
                    correct_answer=answer.correct,
                    explanation=answer.explanation,
                    topic=answer.topic,
                )
            )

        memory = await get_memory(request.user_id)
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        mem_dict = parse_memory(memory)
        mem_dict["Last session"] = timestamp
        
        if mistakes:
            existing_mistakes = mem_dict["Recent mistakes"].strip("[]").replace("'", "").replace('"', '').split(",")
            existing_mistakes.extend(mistakes)
            cleaned_mistakes = [m.strip() for m in existing_mistakes if m.strip()]
            if len(cleaned_mistakes) > 5:
                cleaned_mistakes = cleaned_mistakes[-5:]
            mem_dict["Recent mistakes"] = "[" + ", ".join(cleaned_mistakes) + "]"
        
        existing_subjects = mem_dict["Subjects studied"].strip("[]").replace("'", "").replace('"', '').split(",")
        existing_subjects.append(request.subject)
        cleaned_subjects = list(set([s.strip() for s in existing_subjects if s.strip()]))
        mem_dict["Subjects studied"] = "[" + ", ".join(cleaned_subjects) + "]"

        updated_memory = serialize_memory(mem_dict)
        await save_memory(request.user_id, updated_memory)

        return QuizResult(score=score, total=total, feedback=feedback)
    except Exception as exc:
        logger.exception("Quiz submission failed: %s", exc)
        raise HTTPException(status_code=500, detail="Quiz submission failed")
