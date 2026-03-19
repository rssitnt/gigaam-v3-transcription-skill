# Setup

## Public bootstrap path

1. Run bootstrap:

```bash
python3 {baseDir}/scripts/bootstrap_gigaam_runtime.py
```

This prepares:
- local clone of GigaAM under repo-level `.runtime/GigaAM`
- local venv under repo-level `.runtime/gigaam-venv`
- config file under `skill/config/local.env`
- `ffmpeg` path in one of three modes:
  - reuse from system PATH;
  - fail if `--ffmpeg-mode system` and not found;
  - auto-download a portable/static build if needed

## First smoke run

```bash
python3 {baseDir}/scripts/run_gigaam_transcription.py \
  --input /absolute/path/to/file \
  --env-file {baseDir}/config/local.env
```

## Honest limitations

- Bootstrap uses network access to clone/install dependencies.
- If `ffmpeg` is not in PATH, bootstrap may download a portable/static build into the repo runtime area.
- Large models can take time to download/cache on the first run.
