from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv


def load_project_env() -> None:
    """
    Always load the repository root `.env`, regardless of current working directory.
    """
    project_root = Path(__file__).resolve().parents[2]
    env_path = project_root / ".env"
    # `override=False` so real environment variables win over .env file values.
    load_dotenv(dotenv_path=env_path, override=False)
