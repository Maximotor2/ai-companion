from __future__ import annotations

import argparse
from pathlib import Path

from ai_companion.config import Settings, load_settings
from ai_companion.logging_store import ConversationStore
from ai_companion.goose_client import goose_answer
from ai_companion.memory_store import MemoryStore

_PROJECT_ROOT = Path(__file__).parent.parent.parent

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
    print("Type 'exit' to quit. Type '!remember <fact>' to save a memory.\n")

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
            if fact:
                memory.add(fact)
                print(f"{bot_name}> Got it, I'll remember that.")
            else:
                print(f"{bot_name}> Nothing to remember — try: !remember <fact>")
            continue

        facts = memory.load()
        if facts:
            bullet_list = "\n".join(f"- {f}" for f in facts)
            prompt = f"[Memory]\n{bullet_list}\n\n[User]\n{user_text}"
        else:
            prompt = user_text

        reply = assistant_reply(prompt, settings)
        print(f"{bot_name}> {reply}")
        store.append(session_path, "assistant", reply)


if __name__ == "__main__":
    main()
