# gigaam-v3-transcription-skill

Public standalone AgentSkill project for local transcription through **GigaAM-v3**.

## What this repo is

This repository is meant to become a real GitHub-publishable skill project so another user can:

1. clone the repo;
2. bootstrap a local GigaAM-v3 runtime;
3. package the skill;
4. transcribe a local media file;
5. get transcript artifacts on disk.

## What the skill does

The skill is intended for:
- audio transcription;
- voice note transcription;
- video-audio transcription;
- fallback transcription after public captions fail.

The expected output artifacts are:
- `transcript.txt`
- `transcript.json`
- `final_summary.json`

## Repo layout

- `AGENT.md` — working instruction for coding agents improving this repo
- `docs/public-skill-spec.md` — product definition for the public skill
- `docs/runtime-contract.md` — runtime/config contract
- `skill/` — the actual AgentSkill source
- `skill/SKILL.md` — skill definition
- `skill/scripts/bootstrap_gigaam_runtime.py` — runtime bootstrap script
- `skill/scripts/gigaam_skill_runtime.py` — standalone runtime adapter
- `skill/scripts/run_gigaam_transcription.py` — wrapper used by the skill
- `skill/config/config.env.example` — config example
- `skill/references/setup.md` — setup reference used by the skill
- `artifacts/skill.skill` — packaged skill artifact

## Quick start

### 1. Clone the repo

```bash
git clone <repo-url>
cd gigaam-v3-transcription-skill
```

### 2. Ensure prerequisites

Required local prerequisites:
- Python 3
- `ffmpeg`
- network access for first bootstrap

### 3. Bootstrap the runtime

```bash
python3 skill/scripts/bootstrap_gigaam_runtime.py
```

Expected result:
- local GigaAM clone under `.runtime/GigaAM`
- local venv under `.runtime/gigaam-venv`
- local config at `skill/config/local.env`

### 4. Run a smoke transcription

```bash
python3 skill/scripts/run_gigaam_transcription.py \
  --input /absolute/path/to/local-media-file \
  --env-file skill/config/local.env
```

### 5. Package the skill

From a machine with OpenClaw skill tooling available:

```bash
python3 /home/qwert/.npm-global/lib/node_modules/openclaw/skills/skill-creator/scripts/package_skill.py \
  /mnt/c/projects/automations/gigaam-v3-transcription-skill/skill \
  /mnt/c/projects/automations/gigaam-v3-transcription-skill/artifacts
```

Resulting packaged skill:
- `C:\projects\automations\gigaam-v3-transcription-skill\artifacts\skill.skill`

## Current honest state

Already proven in this repo:
- the skill validates and packages;
- bootstrap creates a project-local runtime;
- cold-start transcription works through that runtime;
- transcript artifacts are written correctly.

Still worth improving:
- replace hardcoded packaging example with repo-local packaging helper;
- add automated tests for bootstrap/config loading;
- add cleaner release workflow for GitHub users outside the current machine.

## Important limitations

- first bootstrap downloads dependencies and can take time;
- local `ffmpeg` is still required;
- model/runtime setup is local-first, not zero-dependency;
- this repo is close to public release quality, but still benefits from final GitHub polish and release instructions.

## Source of truth inside the repo

- public skill: `C:\projects\automations\gigaam-v3-transcription-skill\skill`
- packaged artifact: `C:\projects\automations\gigaam-v3-transcription-skill\artifacts\skill.skill`
- bootstrap reference: `C:\projects\automations\gigaam-v3-transcription-skill\skill\references\setup.md`
