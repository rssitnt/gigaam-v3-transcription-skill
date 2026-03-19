#!/usr/bin/env python3
import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path

DEFAULT_GIGAAM_REPO_URL = "https://github.com/salute-developers/GigaAM.git"
DEFAULT_TORCH_CPU_INDEX_URL = "https://download.pytorch.org/whl/cpu"
DEFAULT_WINDOWS_FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
DEFAULT_LINUX_FFMPEG_URL = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"


def run(command: list[str], *, cwd: Path | None = None) -> None:
    completed = subprocess.run(command, cwd=str(cwd) if cwd else None, text=True, capture_output=True)
    if completed.returncode != 0:
        raise RuntimeError((completed.stderr or completed.stdout or "command failed").strip())


def _download_file(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "gigaam-v3-transcription-skill-bootstrap/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response:
        destination.write_bytes(response.read())


def _find_executable(root: Path, name: str) -> Path | None:
    for path in root.rglob(name):
        if path.is_file():
            return path
    return None


def ensure_ffmpeg(*, repo_root: Path, explicit_ffmpeg: str | None, ffmpeg_mode: str, ffmpeg_url: str | None) -> tuple[str, str]:
    explicit_value = (explicit_ffmpeg or "").strip()
    if explicit_value and explicit_value != "ffmpeg":
        explicit_path = Path(explicit_value)
        if explicit_path.is_absolute() and explicit_path.exists():
            return str(explicit_path), "explicit"
        resolved = shutil.which(explicit_value)
        if resolved:
            return resolved, "explicit"
        if ffmpeg_mode == "system":
            raise RuntimeError(f"Explicit ffmpeg path is not usable: {explicit_value}")

    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg and ffmpeg_mode in {"auto", "system"}:
        return system_ffmpeg, "system"
    if ffmpeg_mode == "system":
        raise RuntimeError("ffmpeg was requested from system PATH, but was not found")

    tools_root = repo_root / ".runtime" / "tools" / "ffmpeg"
    tools_root.mkdir(parents=True, exist_ok=True)

    system_name = platform.system().lower()
    if system_name.startswith("win"):
        archive_url = ffmpeg_url or DEFAULT_WINDOWS_FFMPEG_URL
        archive_path = tools_root / "ffmpeg.zip"
        _download_file(archive_url, archive_path)
        with zipfile.ZipFile(archive_path) as archive:
            archive.extractall(tools_root)
        binary = _find_executable(tools_root, "ffmpeg.exe")
        if not binary:
            raise RuntimeError("Downloaded Windows ffmpeg archive but could not locate ffmpeg.exe")
        return str(binary), "downloaded-windows-portable"

    archive_url = ffmpeg_url or DEFAULT_LINUX_FFMPEG_URL
    archive_path = tools_root / "ffmpeg.tar.xz"
    _download_file(archive_url, archive_path)
    with tarfile.open(archive_path, mode="r:xz") as archive:
        archive.extractall(tools_root)
    binary = _find_executable(tools_root, "ffmpeg")
    if not binary:
        raise RuntimeError("Downloaded Linux ffmpeg archive but could not locate ffmpeg binary")
    os.chmod(binary, 0o755)
    return str(binary), "downloaded-linux-static"


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap local GigaAM-v3 runtime for the public skill")
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--repo-url", default=DEFAULT_GIGAAM_REPO_URL)
    parser.add_argument("--model", default="v3_e2e_rnnt")
    parser.add_argument("--chunk-seconds", default="22")
    parser.add_argument("--ffmpeg-bin", default=shutil.which("ffmpeg") or "ffmpeg")
    parser.add_argument("--ffmpeg-mode", choices=["auto", "system", "download"], default="auto")
    parser.add_argument("--ffmpeg-url")
    args = parser.parse_args()

    skill_root = Path(__file__).resolve().parents[1]
    repo_root = skill_root.parent
    runtime_root = repo_root / ".runtime"
    venv_dir = runtime_root / "gigaam-venv"
    repo_dir = runtime_root / "GigaAM"
    config_dir = skill_root / "config"
    config_path = config_dir / "local.env"

    runtime_root.mkdir(parents=True, exist_ok=True)
    config_dir.mkdir(parents=True, exist_ok=True)

    ffmpeg_path, ffmpeg_source = ensure_ffmpeg(
        repo_root=repo_root,
        explicit_ffmpeg=args.ffmpeg_bin,
        ffmpeg_mode=args.ffmpeg_mode,
        ffmpeg_url=args.ffmpeg_url,
    )

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
                f"GIGAAM_FFMPEG_BIN={ffmpeg_path}",
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
        "ffmpeg_path": ffmpeg_path,
        "ffmpeg_source": ffmpeg_source,
        "next_step": f"Run python3 {Path(__file__).resolve().parent / 'run_gigaam_transcription.py'} --input /absolute/path/to/file --env-file {config_path}",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
