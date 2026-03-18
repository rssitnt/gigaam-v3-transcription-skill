# Runtime contract

## Principle

The public skill must discover runtime from config, not from private machine paths.

## Required config

Expected config values:

- `GIGAAM_LOCAL_PYTHON`
- `GIGAAM_MODEL`
- `GIGAAM_FFMPEG_BIN`
- `GIGAAM_MAX_CHUNK_SECONDS`
- `GIGAAM_OUTPUT_ROOT`

## Config sources

Preferred order:

1. explicit CLI flags
2. env file
3. environment variables

## Required behavior

If runtime is missing:
- stop cleanly
- explain what is missing
- point to setup/bootstrap step

## Output contract

For every successful run, produce:

- `transcript.txt`
- `transcript.json`
- `final_summary.json`

## Packaging contract

The skill itself should remain thin.
Heavy setup logic should live in repo scripts and be referenced from the skill.
