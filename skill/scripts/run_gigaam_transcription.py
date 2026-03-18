#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict

SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = SKILL_ROOT / "output" / "transcripts"
DEFAULT_ENV_FILE = SKILL_ROOT / "config" / "local.env"
RUNTIME_SCRIPT = Path(__file__).resolve().with_name("gigaam_skill_runtime.py")


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
    parser.add_argument("--kind", default="audio")
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

    title = args.title or input_path.stem
    output_dir = Path(args.output_dir) if args.output_dir else output_root / slug(title)
    output_dir.mkdir(parents=True, exist_ok=True)

    text_out = output_dir / "transcript.txt"
    json_out = output_dir / "transcript.json"
    summary_out = output_dir / "final_summary.json"
    meta_out = output_dir / "run_meta.json"

    command = [
        gigaam_python or sys.executable,
        str(RUNTIME_SCRIPT),
        "transcribe",
        "--input",
        str(input_path),
        "--kind",
        args.kind,
        "--title",
        title,
        "--language-hint",
        args.language_hint,
        "--model",
        model,
        "--chunk-seconds",
        chunk_seconds,
        "--ffmpeg-bin",
        ffmpeg_bin,
        "--text-out",
        str(text_out),
        "--json-out",
        str(json_out),
        "--summary-out",
        str(summary_out),
        "--meta-output",
        str(meta_out),
    ]

    if args.print_command:
        print(json.dumps({"command": command}, ensure_ascii=False, indent=2))
        return 0

    if not gigaam_python:
        raise SystemExit("ERROR: GIGAAM_LOCAL_PYTHON is not configured. Run bootstrap_gigaam_runtime.py first or provide config/local.env.")

    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode != 0:
        print(completed.stdout)
        print(completed.stderr, file=sys.stderr)
        raise SystemExit(completed.returncode)

    payload = json.loads(completed.stdout)
    result = {
        "status": "ok",
        "input": str(input_path),
        "output_dir": str(output_dir),
        "text_out": str(text_out),
        "json_out": str(json_out),
        "summary_out": str(summary_out),
        "meta_out": str(meta_out),
        "gigaam_result": payload,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
