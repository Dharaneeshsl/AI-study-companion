from __future__ import annotations

from typing import List
from pydantic import BaseModel


class StudySession(BaseModel):
    subject: str
    time: str
    focus: str


class StudyDay(BaseModel):
    day: str
    sessions: List[StudySession]


class StudyPlanRequest(BaseModel):
    user_id: str


class StudyPlanResponse(BaseModel):
    plan: List[StudyDay]
