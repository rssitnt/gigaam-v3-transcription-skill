# Setup

## Public bootstrap path

1. Ensure `ffmpeg` is installed and reachable in PATH.
2. Run:

```bash
python3 {baseDir}/scripts/bootstrap_gigaam_runtime.py
```

This prepares:
- local clone of GigaAM under `skill/.runtime/GigaAM`
- local venv under `skill/.runtime/gigaam-venv`
- config file under `skill/config/local.env`

## First smoke run

```bash
python3 {baseDir}/scripts/run_gigaam_transcription.py \
  --input /absolute/path/to/file \
  --env-file {baseDir}/config/local.env
```

## Honest limitations

- The user still needs local `ffmpeg`.
- The bootstrap uses network access to clone/install dependencies.
- Large models can take time to download/cache on the first run.
