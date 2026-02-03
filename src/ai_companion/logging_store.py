from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class Turn:
    role: str  # "user" | "assistant" | "system"
    content: str
    ts_iso: str


class ConversationStore:
    def __init__(self, base_dir: str = "data") -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def new_session_path(self) -> Path:
        now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        return self.base_dir / f"session_{now}.jsonl"

    def append(self, path: Path, role: str, content: str) -> None:
        turn = Turn(role=role, content=content, ts_iso=datetime.now(timezone.utc).isoformat())
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(turn), ensure_ascii=False) + "\n")
