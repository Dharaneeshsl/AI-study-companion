import json
import logging
import re
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from core.security import get_current_user
from models.quiz import (
    QuizAnswer,
    QuizFeedback,
    QuizQuestion,
    QuizRequest,
    QuizResponse,
    QuizResult,
    QuizSubmitRequest,
)
from services.groq_client import call_groq
from services.hindsight import (
    get_memory,
    parse_memory,
    parse_memory_list,
    save_memory,
    serialize_memory,
    serialize_memory_list,
)
from core.security import get_current_user


logger = logging.getLogger("router.quiz")
router = APIRouter(prefix="/api/quiz", tags=["quiz"])


def _build_quiz_prompt(memory: str, subject: str) -> str:
    return (
        "You are an AI tutor creating a personalized quiz.\n"
        "Use the student's memory to target weak topics in the given subject.\n"
        "Prioritize topics explicitly mentioned as weak or recently mistaken.\n"
        "Return ONLY valid JSON in this format:\n"
        '{"questions": [{"id": "q1", "question": "...", "options": ["A", "B", "C", "D"], '
        '"answer": "A", "explanation": "...", "topic": "..."}]}\n\n'
        f"Subject: {subject}\nMEMORY CONTEXT:\n{memory}\n"
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


def _validate_questions(questions: List[QuizQuestion]) -> List[QuizQuestion]:
    if len(questions) != 5:
        raise ValueError("Expected 5 questions")

    for question in questions:
        if len(question.options) != 4:
            raise ValueError("Each question must have exactly 4 options")
        if question.answer not in question.options:
            raise ValueError("Correct answer must be one of the options")
    return questions


@router.post("/generate", response_model=QuizResponse)
async def generate_quiz(
    request: QuizRequest,
    current_user=Depends(get_current_user),
) -> QuizResponse:
    try:
        user_id = current_user["user_id"]
        memory = await get_memory(user_id)
        try:
            data = _extract_json(raw)
            questions_raw = data.get("questions", [])
            questions = _validate_questions([QuizQuestion(**q) for q in questions_raw])
        except Exception:
            logger.warning("Failed to parse quiz JSON; using fallback", exc_info=True)
            questions = _fallback_questions(request.subject)
        return QuizResponse(questions=questions)
    except Exception as exc:
        logger.exception("Quiz generation failed: %s", exc)
        raise HTTPException(status_code=500, detail="Quiz generation failed") from exc


@router.post("/submit", response_model=QuizResult)
async def submit_quiz(
    request: QuizSubmitRequest,
    current_user=Depends(get_current_user),
) -> QuizResult:
    try:
        feedback: List[QuizFeedback] = []
        mistakes: list[str] = []
        score = 0

        for answer in request.answers:
            is_correct = answer.selected.strip() == answer.correct.strip()
            score += int(is_correct)
            if not is_correct:
                mistakes.append(f"{request.subject} - {answer.topic}: missed '{answer.question}'")
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

        user_id = current_user["user_id"]
        memory = await get_memory(user_id)
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        mem_dict = parse_memory(memory)
        mem_dict["Last session"] = timestamp

        if mistakes:
            existing_mistakes = parse_memory_list(mem_dict["Recent mistakes"])
            cleaned_mistakes = [*existing_mistakes, *mistakes][-5:]
            mem_dict["Recent mistakes"] = serialize_memory_list(cleaned_mistakes)

        existing_subjects = parse_memory_list(mem_dict["Subjects studied"])
        cleaned_subjects = list(dict.fromkeys([*existing_subjects, request.subject]))
        mem_dict["Subjects studied"] = serialize_memory_list(cleaned_subjects)

        updated_memory = serialize_memory(mem_dict)
        await save_memory(user_id, updated_memory)

        return QuizResult(score=score, total=total, feedback=feedback)
    except Exception as exc:
        logger.exception("Quiz submission failed: %s", exc)
        raise HTTPException(status_code=500, detail="Quiz submission failed") from exc
