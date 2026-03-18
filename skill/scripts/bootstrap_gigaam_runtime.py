#!/usr/bin/env python3
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_GIGAAM_REPO_URL = "https://github.com/salute-developers/GigaAM.git"
DEFAULT_TORCH_CPU_INDEX_URL = "https://download.pytorch.org/whl/cpu"


def run(command: list[str], *, cwd: Path | None = None) -> None:
    completed = subprocess.run(command, cwd=str(cwd) if cwd else None, text=True, capture_output=True)
    if completed.returncode != 0:
        raise RuntimeError((completed.stderr or completed.stdout or "command failed").strip())


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap local GigaAM-v3 runtime for the public skill")
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--repo-url", default=DEFAULT_GIGAAM_REPO_URL)
    parser.add_argument("--model", default="v3_e2e_rnnt")
    parser.add_argument("--chunk-seconds", default="22")
    parser.add_argument("--ffmpeg-bin", default=shutil.which("ffmpeg") or "ffmpeg")
    args = parser.parse_args()

    skill_root = Path(__file__).resolve().parents[1]
    runtime_root = skill_root / ".runtime"
    venv_dir = runtime_root / "gigaam-venv"
    repo_dir = runtime_root / "GigaAM"
    config_dir = skill_root / "config"
    config_path = config_dir / "local.env"

    runtime_root.mkdir(parents=True, exist_ok=True)
    config_dir.mkdir(parents=True, exist_ok=True)

    if not repo_dir.exists():
        run(["git", "clone", args.repo_url, str(repo_dir)])

    if not venv_dir.exists():
        run([args.python, "-m", "venv", str(venv_dir)])

    venv_python = venv_dir / "bin" / "python"
    pip_base = [str(venv_python), "-m", "pip"]
    run(pip_base + ["install", "--upgrade", "pip", "setuptools", "wheel"])
    run(pip_base + ["install", "hydra-core==1.3.*", "numpy==2.*", "omegaconf==2.3.*", "onnx==1.19.*", "onnxruntime==1.23.*", "sentencepiece", "tqdm"])
    run(pip_base + ["install", "--index-url", DEFAULT_TORCH_CPU_INDEX_URL, "torch>=2.5,<2.9", "torchaudio>=2.5,<2.9"])
    run(pip_base + ["install", "--no-deps", "-e", str(repo_dir)])

    config_path.write_text(
        "\n".join(
            [
                f"GIGAAM_LOCAL_PYTHON={venv_python}",
                f"GIGAAM_MODEL={args.model}",
                f"GIGAAM_FFMPEG_BIN={args.ffmpeg_bin}",
                f"GIGAAM_MAX_CHUNK_SECONDS={args.chunk_seconds}",
                f"GIGAAM_OUTPUT_ROOT={skill_root / 'output' / 'transcripts'}",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = {
        "status": "ok",
        "skill_root": str(skill_root),
        "runtime_root": str(runtime_root),
        "repo_dir": str(repo_dir),
        "venv_python": str(venv_python),
        "config_path": str(config_path),
        "next_step": f"Run python3 {Path(__file__).resolve().parent / 'run_gigaam_transcription.py'} --input /absolute/path/to/file --env-file {config_path}",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
