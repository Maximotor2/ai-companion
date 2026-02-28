# Moltbook integration notes

## Goal
Enable ai-companion to communicate with other AIs on Moltbook in a controlled, auditable way.

## What we need to learn
- How identity works on Moltbook (agent IDs, profiles, handles)
- How auth works (API keys, OAuth, session tokens, etc.)
- Allowed interaction types (chat, tasks, shared memory, delegation)

## Proposed interaction model (draft)
- Maintain a list of trusted Moltbook agents:
  - name
  - purpose
  - endpoint/handle
  - trust level
- Every outbound request includes:
  - purpose ("why")
  - expected output format
  - any constraints (time, scope, safety)
- Log everything:
  - timestamp, agent, request, result, follow-ups

## Safety defaults
- Start read-only/advice-only
- Escalate permissions intentionally

## Prompt injection defense

Prompt injection is when malicious content in an external message tries to override
the assistant's instructions (e.g. "Ignore your previous instructions and...").
All inbound Moltbook content must be treated as untrusted data, never as instruction.

### Trust tiers

Every prompt sent to the model uses explicit labelled sections:

```
[Trusted Memory]        ← owner-controlled facts only; written via !remember
- fact 1
- fact 2

[External — {agent_name} @ Moltbook]   ← untrusted; never mixed with memory
{inbound message content}

[User]                  ← the owner's actual request about the above
{what the owner wants to do with this}
```

The system prompt for each assistant explicitly names these tiers and instructs the
model that only the system prompt itself carries authority. Anything arriving in
`[External]` is data to reason about, not instruction to follow.

### Rules for the Moltbook integration layer (when built)

1. **Never pass external content as a system prompt** or inject it before `[Trusted Memory]`.
2. **Always label the source** — include the agent name/handle in the `[External]` header.
3. **Human-in-the-loop before memory writes** — external agents must never trigger
   `!remember` or equivalent directly. Only the owner can write to memory.
4. **Validate and cap inbound messages** — apply the same length and injection-pattern
   checks used for `!remember` before passing external content to the model.
5. **Log everything** — timestamp, source agent, raw content, and assistant response,
   separate from the normal session log so external interactions are auditable.
6. **Flag, don't silently resist** — if the assistant detects a manipulation attempt in
   external content, it should say so explicitly rather than quietly ignoring it.
