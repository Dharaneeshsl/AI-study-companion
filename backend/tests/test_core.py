import os
import sys
import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

os.environ.setdefault("SECRET_KEY", "test-secret-key-for-unit-tests")
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from bson import ObjectId
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError

from core.security import get_password_hash
from routers.auth import login, signup
from schemas.user import UserCreate
from services.hindsight import (
    DEFAULT_MEMORY,
    parse_list_value,
    parse_memory,
    record_study_activity,
    serialize_memory,
)
from models.quiz import QuizRequest, QuizSubmitRequest


class FakeUsers:
    def __init__(self, user=None):
        self.user = user
        self.inserted = None

    async def find_one(self, _query):
        return self.user

    async def insert_one(self, document):
        self.inserted = document
        return SimpleNamespace(inserted_id=ObjectId())


class FakeDb:
    def __init__(self, user=None):
        self.users = FakeUsers(user)


class CoreBehaviorTests(unittest.IsolatedAsyncioTestCase):
    def test_memory_round_trip_and_legacy_list_parsing(self):
        memory = parse_memory(DEFAULT_MEMORY)
        memory["Learning insights"] = '["Unicode insight: café"]'
        restored = parse_memory(serialize_memory(memory))
        self.assertEqual(parse_list_value(restored["Learning insights"]), ["Unicode insight: café"])
        self.assertEqual(restored["Study streak"], "0 days")

    def test_streak_increments_on_consecutive_days_and_not_same_day(self):
        memory = parse_memory(DEFAULT_MEMORY)
        record_study_activity(memory, "2026-08-17 09:00 UTC")
        self.assertEqual(memory["Study streak"], "1 days")
        record_study_activity(memory, "2026-08-18 09:00 UTC")
        self.assertEqual(memory["Study streak"], "2 days")
        record_study_activity(memory, "2026-08-18 12:00 UTC")
        self.assertEqual(memory["Study streak"], "2 days")

    async def test_signup_and_login_flow(self):
        db = FakeDb()
        user = UserCreate(username="Study_User", email="Student@Example.com", password="strongpass1")
        response = await signup(user, db=db)
        self.assertEqual(response["email"], "student@example.com")
        self.assertTrue(db.users.inserted["is_active"])

        stored = {**db.users.inserted, "_id": ObjectId()}
        login_db = FakeDb(stored)
        form = OAuth2PasswordRequestForm(username="study_user", password="strongpass1")
        token = await login(request=None, form_data=form, db=login_db)
        self.assertEqual(token["token_type"], "bearer")
        self.assertTrue(token["access_token"])

    def test_password_and_quiz_validation(self):
        with self.assertRaises(ValidationError):
            UserCreate(username="ab", email="bad@example.com", password="short")
        request = QuizRequest(subject="Physics")
        self.assertEqual(request.subject, "Physics")
        with self.assertRaises(ValidationError):
            QuizSubmitRequest(subject="Physics", answers=[])


if __name__ == "__main__":
    unittest.main()
