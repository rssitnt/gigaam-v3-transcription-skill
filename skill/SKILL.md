---
name: gigaam-v3-transcription
description: Local transcription of audio, voice notes, video-audio, and extracted YouTube audio through GigaAM-v3. Use when an agent needs a local ASR path for media files and wants transcript artifacts on disk. Best for absolute local media paths and artifact-first workflows.
---

# GigaAM-v3 transcription

Use this skill to transcribe a local media file through a local GigaAM-v3 runtime.

## Quick start

1. Ensure the media file is local and the path is absolute.
2. Ensure the runtime config is prepared for this repo.
3. Run:
   - `python3 {baseDir}/scripts/run_gigaam_transcription.py --input /absolute/path/to/file`
4. Use the returned artifact paths as source of truth.

## Use this skill for

- local audio transcription
- voice note transcription
- video-audio transcription
- fallback transcription after public captions fail

## Workflow

### 1. Validate input

Require a local absolute path.

### 2. Run the wrapper

```bash
python3 {baseDir}/scripts/run_gigaam_transcription.py --input /absolute/path/to/file
```

Optional flags:
- `--title`
- `--language-hint`
- `--kind`
- `--output-dir`
- `--env-file`

### 3. Trust artifacts

Use these artifact files:
- `transcript.txt`
- `transcript.json`
- `final_summary.json`

### 4. Report honestly

If runtime/config/bootstrap is missing, report the exact blocker and point to setup.
