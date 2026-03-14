from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

def _load_dotenv(dotenv_path: Path) -> None:
    """Load key=value pairs from a .env file into os.environ.

    Supports:
    - Single-line values:   KEY=value
    - Quoted multiline:     KEY="line1\nline2"
    - Comments (#) and blank lines are skipped
    - Already-set env vars are not overwritten
    """
    if not dotenv_path.exists():
        return
    text = dotenv_path.read_text(encoding="utf-8")
    i = 0
    lines = text.splitlines()
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith("#") or "=" not in line:
            i += 1
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        # Collect multiline quoted value
        if value.startswith('"') and not value.endswith('"'):
            parts = [value[1:]]  # strip opening quote
            i += 1
            while i < len(lines):
                chunk = lines[i]
                if chunk.rstrip().endswith('"'):
                    parts.append(chunk.rstrip()[:-1])  # strip closing quote
                    i += 1
                    break
                parts.append(chunk)
                i += 1
            value = "\n".join(parts)
        elif value.startswith('"') and value.endswith('"') and len(value) > 1:
            value = value[1:-1]  # strip surrounding quotes
        if key and key not in os.environ:
            os.environ[key] = value
        i += 1


@dataclass(frozen=True)
class Settings:
    llm_provider: str | None
    llm_model: str | None
    llm_api_key: str | None
    moltbook_api_url: str | None
    moltbook_api_key: str | None
    identity_name: str | None
    identity_system_prompt: str | None


def load_settings(project_root: Path | None = None, assistant: str | None = None) -> Settings:
    """Load settings from .env then an optional per-assistant file, then environment variables."""
    root = project_root or Path(__file__).parent.parent.parent
    _load_dotenv(root / ".env")
    if assistant:
        _load_dotenv(root / "assistants" / f"{assistant}.env")
    return Settings(
        llm_provider=os.getenv("LLM_PROVIDER"),
        llm_model=os.getenv("LLM_MODEL"),
        llm_api_key=os.getenv("LLM_API_KEY"),
        moltbook_api_url=os.getenv("MOLTBOOK_API_URL"),
        moltbook_api_key=os.getenv("MOLTBOOK_API_KEY"),
        identity_name=os.getenv("IDENTITY_NAME"),
        identity_system_prompt=os.getenv("IDENTITY_SYSTEM_PROMPT"),
    )
