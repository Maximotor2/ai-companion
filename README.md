# ai-companion

Some personal AI assistants I control: identity, memory, tools, boundaries—built to collaborate with other AIs.

## What’s here
- docs/vision.md — what this assistant is / isn’t
- docs/roadmap.md — near-term milestones
- docs/moltbook-integration.md — how it connects to Moltbook AIs if desired
- src/ — Python package (`ai_companion`): config, goose client, conversation store, CLI

## Safety defaults
- Secrets are never committed (.env is ignored)
- Integrations are documented before they’re enabled
- Human-in-the-loop for actions that matter
