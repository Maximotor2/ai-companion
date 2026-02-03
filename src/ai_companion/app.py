from __future__ import annotations

from ai_companion.config import load_settings
from ai_companion.logging_store import ConversationStore


def assistant_reply(user_text: str) -> str:
    """
    Placeholder "brain".
    Next step: swap this with an LLM provider and/or Moltbook agent calls.
    """
    user_text = user_text.strip()
    if not user_text:
        return "Say something and I’ll respond."

    # tiny helpful behavior for now
    if user_text.lower() in {"exit", "quit"}:
        return "Goodbye! (Type Ctrl+C if you’re stuck in a loop.)"

    return f"I heard: {user_text}\n\n(Next: we’ll plug in your model + Moltbook.)"


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
