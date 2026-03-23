from __future__ import annotations

from typing import List
from pydantic import BaseModel


class QuizQuestion(BaseModel):
    id: str
    question: str
    options: List[str]
    answer: str
    explanation: str
    topic: str


class QuizRequest(BaseModel):
    user_id: str
    subject: str


class QuizResponse(BaseModel):
    questions: List[QuizQuestion]


class QuizAnswer(BaseModel):
    id: str
    selected: str
    correct: str
    question: str
    explanation: str
    topic: str


class QuizSubmitRequest(BaseModel):
    user_id: str
    subject: str
    answers: List[QuizAnswer]


class QuizFeedback(BaseModel):
    id: str
    correct: bool
    selected: str
    correct_answer: str
    explanation: str
    topic: str


class QuizResult(BaseModel):
    score: int
    total: int
    feedback: List[QuizFeedback]
