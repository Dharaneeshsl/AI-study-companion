from typing import List

from pydantic import BaseModel, Field


class QuizQuestion(BaseModel):
    id: str
    question: str
    options: List[str]
    answer: str
    explanation: str
    topic: str


class QuizRequest(BaseModel):
    subject: str = Field(min_length=1, max_length=120)


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
    subject: str = Field(min_length=1, max_length=120)
    answers: List[QuizAnswer] = Field(min_length=1, max_length=50)


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
