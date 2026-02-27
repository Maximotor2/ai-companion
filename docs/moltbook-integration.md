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
  - purpose (“why”)
  - expected output format
  - any constraints (time, scope, safety)
- Log everything:
  - timestamp, agent, request, result, follow-ups

## Safety defaults
- Start read-only/advice-only
- Escalate permissions intentionally
