from __future__ import annotations

from ai_companion.config import load_settings
from ai_companion.logging_store import ConversationStore
from ai_companion.goose_client import goose_answer

def assistant_reply(user_text: str) -> str:
    user_text = user_text.strip()
    if not user_text:
        return "Say something and I’ll respond."

    if user_text.lower() in {"exit", "quit"}:
        return "Goodbye."

    return goose_answer(user_text)


def main() -> None:
    settings = load_settings()
    _ = settings  # reserved for next step

    store = ConversationStore(base_dir="data")
    session_path = store.new_session_path()

    print("ai-companion CLI")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            user_text = input("you> ")
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        store.append(session_path, "user", user_text)

        if user_text.strip().lower() in {"exit", "quit"}:
            reply = "Bye."
            print(f"bot> {reply}")
            store.append(session_path, "assistant", reply)
            break

        reply = assistant_reply(user_text)
        print(f"bot> {reply}")
        store.append(session_path, "assistant", reply)


if __name__ == "__main__":
    main()
