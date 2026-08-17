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
    pass


class StudyPlanResponse(BaseModel):
    plan: List[StudyDay]
