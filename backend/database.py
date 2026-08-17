import os

from motor.motor_asyncio import AsyncIOMotorClient

from core.env import load_project_env


load_project_env()

MONGODB_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("DATABASE_NAME", "studycompanion")

client = AsyncIOMotorClient(MONGODB_URL)
database = client[MONGODB_DB_NAME]


# Dependency
async def get_db():
    yield database
