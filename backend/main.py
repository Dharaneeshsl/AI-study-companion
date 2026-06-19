from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load .env before importing modules that read environment variables.
from core.env import load_project_env

load_project_env()

from routers.chat import router as chat_router
from routers.quiz import router as quiz_router
from routers.study_plan import router as study_plan_router
from routers.auth import router as auth_router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("ai-study-companion")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Backend starting up")
    yield
    logger.info("Backend shutting down")


app = FastAPI(lifespan=lifespan)

allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(quiz_router)
app.include_router(study_plan_router)
app.include_router(auth_router)
