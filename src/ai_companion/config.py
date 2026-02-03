from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    llm_provider: str | None
    llm_api_key: str | None
    moltbook_api_url: str | None
    moltbook_api_key: str | None


def load_settings() -> Settings:
    """
    Load settings from environment variables.
    (We will later add .env loading, but env vars work everywhere.)
    """
    return Settings(
        llm_provider=os.getenv("LLM_PROVIDER"),
        llm_api_key=os.getenv("LLM_API_KEY"),
        moltbook_api_url=os.getenv("MOLTBOOK_API_URL"),
        moltbook_api_key=os.getenv("MOLTBOOK_API_KEY"),
    )
