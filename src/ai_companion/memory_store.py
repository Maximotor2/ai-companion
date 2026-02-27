from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class Fact:
    fact: str
    ts_iso: str


class MemoryStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> list[str]:
        if not self.path.exists():
            return []
        facts: list[str] = []
        with self.path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    facts.append(json.loads(line)["fact"])
                except (json.JSONDecodeError, KeyError):
                    pass
        return facts

    def add(self, fact: str) -> None:
        entry = Fact(fact=fact, ts_iso=datetime.now(timezone.utc).isoformat())
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(entry), ensure_ascii=False) + "\n")
