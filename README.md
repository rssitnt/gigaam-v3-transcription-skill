# gigaam-v3-transcription-skill

GitHub-ready project for a public AgentSkill that provides local transcription through GigaAM-v3.

## Goal

Build a **real distributable skill for agents** so another user can clone/download the repo, follow setup, package the `.skill`, and use local GigaAM-v3 transcription without hardcoded machine-specific paths.

## What this project should become

- standalone skill project
- GitHub-publishable
- packaged `.skill` artifact
- bootstrap/setup flow
- smoke test
- no dependency on `/home/qwert/.openclaw/projects/live-rollout-check/...`

## Current project structure

- `AGENT.md` — main instruction for the coding agent working on this repo
- `docs/public-skill-spec.md` — product and packaging requirements
- `docs/runtime-contract.md` — expected runtime/config contract
- `skill/SKILL.md` — public skill draft
- `skill/scripts/run_gigaam_transcription.py` — standalone wrapper draft
- `skill/scripts/bootstrap_gigaam_runtime.py` — runtime bootstrap draft
- `examples/config.env.example` — example config
- `tests/` — initial test placeholders

## Success criteria

This repo is successful when:

1. a user can clone it;
2. follow setup instructions;
3. configure local runtime once;
4. package the skill;
5. run transcription on a local media file;
6. get transcript artifacts without editing machine-specific absolute paths in code.
