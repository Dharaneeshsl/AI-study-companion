# AI Study Companion

AI Study Companion is a full-stack web app that provides personalized tutoring, quizzes, and study plans using long-term memory. The backend reads the student’s memory, injects relevant context into Groq prompts, and records learning activity with a MongoDB fallback when Hindsight is unavailable.

## Features

The application includes a memory-aware chat tutor, personalized five-question quizzes targeting weak topics, weekly study-plan generation, case-insensitive account authentication, password validation, a real study streak, and a backend health endpoint at `/health`.

## Configuration

Copy `.env.example` to `.env` and replace the placeholders before starting the application. `SECRET_KEY` and `GROQ_API_KEY` are required for the intended experience. `DATABASE_URL`, `DATABASE_NAME`, Hindsight settings, `CORS_ORIGINS`, and `NEXT_PUBLIC_API_URL` are documented in the template. Do not commit `.env` or real secrets.

## Docker startup

Run the complete stack with:

```bash
docker compose --env-file .env up --build
```

Open `http://localhost:3000` in a browser. The backend is exposed at `http://localhost:8001`; its readiness endpoint is `http://localhost:8001/health` and should return `{\"status\":\"ok\"}`.

## Local development without Docker

Install Python 3.11 or newer and Node.js 20 or newer. Then run the backend and frontend in separate terminals:

```bash
cp .env.example .env
python3 -m venv .venv
. .venv/bin/activate
pip install -r backend/requirements.txt
cd backend
uvicorn main:app --reload --port 8000
```

In a second terminal:

```bash
cd frontend
npm ci
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

A local MongoDB instance is required for local development unless the configured Hindsight service is available. Open `http://localhost:3000` after both processes start.

## Hindsight integration

The Docker stack includes Hindsight on `http://localhost:8888`. Its LLM configuration uses `GROQ_API_KEY`, `HINDSIGHT_API_LLM_MODEL`, and `HINDSIGHT_API_LLM_API_KEY`; set the latter to the same value as `GROQ_API_KEY` when required by the Hindsight deployment.

## Memory behavior

Every authenticated request reads the latest memory for that user. Chat insights are stored under `Learning insights` rather than being misclassified as weak topics. Chat and quiz activity updates `Last session` and increments the `Study streak` once per UTC calendar day. Quiz mistakes and studied subjects remain separately tracked, and Hindsight falls back to MongoDB when remote memory is unavailable.

## Verification

Backend checks:

```bash
python3 -m compileall backend
python3 -m unittest discover -s backend/tests -v
```

Frontend checks:

```bash
cd frontend
npm ci
npm run typecheck
npm run build
```

The CI workflow runs the same compile, unit-test, type-check, and production-build checks. The CD workflow builds and publishes backend and frontend images to GHCR on `main` or manual dispatch.

## Documentation links

- [Hindsight](https://hindsight.vectorize.io)
- [Groq Console](https://console.groq.com)
