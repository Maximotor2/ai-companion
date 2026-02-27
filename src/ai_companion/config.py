from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _load_dotenv(dotenv_path: Path) -> None:
    """Load key=value pairs from a .env file into os.environ (skips already-set keys)."""
    if not dotenv_path.exists():
        return
    with dotenv_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            if key and key not in os.environ:
                os.environ[key] = value


@dataclass(frozen=True)
class Settings:
    llm_provider: str | None
    llm_api_key: str | None
    moltbook_api_url: str | None
    moltbook_api_key: str | None


def load_settings(project_root: Path | None = None) -> Settings:
    """Load settings from a .env file (if present) then environment variables."""
    root = project_root or Path(__file__).parent.parent.parent
    _load_dotenv(root / ".env")
    return Settings(
        llm_provider=os.getenv("LLM_PROVIDER"),
        llm_api_key=os.getenv("LLM_API_KEY"),
        moltbook_api_url=os.getenv("MOLTBOOK_API_URL"),
        moltbook_api_key=os.getenv("MOLTBOOK_API_KEY"),
    )
