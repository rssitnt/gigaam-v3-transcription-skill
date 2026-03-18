#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict

DEFAULT_OUTPUT_ROOT = Path("./output/transcripts")
DEFAULT_ENV_FILE = Path("./examples/config.env.example")


def load_env_file(path: Path) -> Dict[str, str]:
    values: Dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def env_value(key: str, loaded: Dict[str, str]) -> str:
    return os.environ.get(key) or loaded.get(key) or ""


def slug(value: str) -> str:
    safe = "".join(ch.lower() if ch.isalnum() else "-" for ch in value)
    while "--" in safe:
        safe = safe.replace("--", "-")
    return safe.strip("-") or "input"


def main() -> int:
    parser = argparse.ArgumentParser(description="Standalone wrapper for GigaAM-v3 transcription skill")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir")
    parser.add_argument("--title")
    parser.add_argument("--language-hint", default="ru")
    parser.add_argument("--kind")
    parser.add_argument("--env-file", default=str(DEFAULT_ENV_FILE))
    parser.add_argument("--print-command", action="store_true")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.is_absolute():
        raise SystemExit("ERROR: --input must be an absolute local path")
    if not input_path.exists():
        raise SystemExit(f"ERROR: input file not found: {input_path}")

    env_path = Path(args.env_file)
    loaded = load_env_file(env_path)
    gigaam_python = env_value("GIGAAM_LOCAL_PYTHON", loaded)
    ffmpeg_bin = env_value("GIGAAM_FFMPEG_BIN", loaded) or "ffmpeg"
    model = env_value("GIGAAM_MODEL", loaded) or "v3_e2e_rnnt"
    chunk_seconds = env_value("GIGAAM_MAX_CHUNK_SECONDS", loaded) or "22"
    output_root = Path(env_value("GIGAAM_OUTPUT_ROOT", loaded) or str(DEFAULT_OUTPUT_ROOT))

    if not gigaam_python:
        raise SystemExit("ERROR: GIGAAM_LOCAL_PYTHON is not configured. Prepare config/env first.")

    runtime_entrypoint = Path(gigaam_python).resolve().parent.parent / "lib-placeholder"
    del runtime_entrypoint  # explicit no-op; public skill should not pretend to know private runtime layout

    title = args.title or input_path.stem
    output_dir = Path(args.output_dir) if args.output_dir else output_root / slug(title)
    output_dir.mkdir(parents=True, exist_ok=True)

    text_out = output_dir / "transcript.txt"
    json_out = output_dir / "transcript.json"
    summary_out = output_dir / "final_summary.json"

    command = [
        sys.executable,
        "-m",
        "gigaam_skill_runtime_stub",
        "--input",
        str(input_path),
        "--python",
        gigaam_python,
        "--model",
        model,
        "--ffmpeg-bin",
        ffmpeg_bin,
        "--chunk-seconds",
        chunk_seconds,
        "--language-hint",
        args.language_hint,
        "--text-out",
        str(text_out),
        "--json-out",
        str(json_out),
        "--summary-out",
        str(summary_out),
    ]
    if args.kind:
        command.extend(["--kind", args.kind])

    if args.print_command:
        print(json.dumps({"command": command}, ensure_ascii=False, indent=2))
        return 0

    note = {
        "status": "wrapper-draft",
        "message": "This public repo still needs the final runtime adapter module instead of the private local entrypoint.",
        "input": str(input_path),
        "output_dir": str(output_dir),
        "suggested_command": command,
    }
    print(json.dumps(note, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
