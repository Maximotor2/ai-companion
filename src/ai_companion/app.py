from __future__ import annotations

import argparse
from pathlib import Path

from ai_companion.config import Settings, load_settings
from ai_companion.logging_store import ConversationStore
from ai_companion.goose_client import goose_answer
from ai_companion.memory_store import MemoryStore
from ai_companion.search_client import brave_search

_PROJECT_ROOT = Path(__file__).parent.parent.parent

_REMEMBER_MAX_LEN = 500
_INJECTION_PATTERNS = [
    "ignore previous", "ignore your", "ignore all",
    "new directive", "new instruction", "new role",
    "system:", "system prompt",
    "override", "disregard",
    "forget everything", "forget your",
    "you are now", "your new role",
    "act as",
]


def _looks_like_injection(text: str) -> bool:
    lower = text.lower()
    return any(p in lower for p in _INJECTION_PATTERNS)


def assistant_reply(user_text: str, settings: Settings) -> str:
    user_text = user_text.strip()
    if not user_text:
        return "Say something and I’ll respond."

    return goose_answer(user_text, settings)


def main() -> None:
    parser = argparse.ArgumentParser(description="ai-companion CLI")
    parser.add_argument("--assistant", help="Assistant profile to load (e.g. monique, andrew)")
    args = parser.parse_args()

    settings = load_settings(project_root=_PROJECT_ROOT, assistant=args.assistant)

    bot_name = settings.identity_name or "bot"
    assistant_dir = _PROJECT_ROOT / "data" / (settings.identity_name or "default")

    store = ConversationStore(base_dir=assistant_dir)
    session_path = store.new_session_path()
    memory = MemoryStore(path=assistant_dir / "memory.jsonl")

    print("ai-companion CLI")
    print("Type 'exit' to quit.")
    print("  !remember <fact>   — save a fact to memory")
    print("  !search <query>    — web search, then discuss with assistant\n")

    while True:
        try:
            user_text = input("you> ")
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        store.append(session_path, "user", user_text)

        if user_text.strip().lower() in {"exit", "quit"}:
            reply = "Bye."
            print(f"{bot_name}> {reply}")
            store.append(session_path, "assistant", reply)
            break

        if user_text.strip().lower().startswith("!remember "):
            fact = user_text.strip()[len("!remember "):].strip()
            if not fact:
                print(f"{bot_name}> Nothing to remember — try: !remember <fact>")
            elif len(fact) > _REMEMBER_MAX_LEN:
                print(f"{bot_name}> Too long to store (max {_REMEMBER_MAX_LEN} chars). Please summarize it.")
            elif _looks_like_injection(fact):
                print(f"{bot_name}> That looks like an instruction rather than a fact. I won't store it.")
            else:
                memory.add(fact)
                print(f"{bot_name}> Got it, I'll remember that.")
            continue

        if user_text.strip().lower().startswith("!search "):
            query = user_text.strip()[len("!search "):].strip()
            if not query:
                print(f"{bot_name}> Nothing to search — try: !search <query>")
                continue
            print(f"{bot_name}> Searching for: {query} ...")
            try:
                search_results = brave_search(query)
            except (ValueError, RuntimeError) as exc:
                print(f"{bot_name}> [search error] {exc}")
                continue
            facts = memory.load()
            parts: list[str] = []
            if facts:
                bullet_list = "\n".join(f"- {f}" for f in facts)
                parts.append(f"[Trusted Memory]\n{bullet_list}")
            parts.append(f"[Search Results — Brave Web Search]\n{search_results}")
            parts.append(f"[User]\nI searched for: {query}\nWhat do you make of these results?")
            prompt = "\n\n".join(parts)
            reply = assistant_reply(prompt, settings)
            print(f"{bot_name}> {reply}")
            store.append(session_path, "assistant", reply)
            continue

        facts = memory.load()
        if facts:
            bullet_list = "\n".join(f"- {f}" for f in facts)
            prompt = f"[Trusted Memory]\n{bullet_list}\n\n[User]\n{user_text}"
        else:
            prompt = user_text

        reply = assistant_reply(prompt, settings)
        print(f"{bot_name}> {reply}")
        store.append(session_path, "assistant", reply)


if __name__ == "__main__":
    main()
