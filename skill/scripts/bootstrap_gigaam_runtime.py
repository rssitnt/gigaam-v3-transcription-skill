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


def run(command: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(command, cwd=str(cwd) if cwd else None, text=True, capture_output=True)
    if completed.returncode != 0:
        raise RuntimeError((completed.stderr or completed.stdout or "command failed").strip())
    return completed


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


def _detect_env_id() -> str:
    system_name = platform.system().lower()
    if system_name.startswith("win"):
        return "windows-host"
    if Path("/.dockerenv").exists():
        return "linux-container"
    cgroup = Path("/proc/1/cgroup")
    if cgroup.exists():
        text = cgroup.read_text(encoding="utf-8", errors="ignore").lower()
        if any(token in text for token in ["docker", "containerd", "kubepods"]):
            return "linux-container"
    if "microsoft" in platform.release().lower():
        return "linux-wsl"
    return "linux-host"


def _venv_python_path(venv_dir: Path) -> Path:
    if platform.system().lower().startswith("win"):
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _venv_is_healthy(venv_dir: Path) -> tuple[bool, str]:
    python_path = _venv_python_path(venv_dir)
    if not python_path.exists():
        return False, f"missing python at {python_path}"
    probe = subprocess.run([str(python_path), "-m", "pip", "--version"], text=True, capture_output=True)
    if probe.returncode != 0:
        return False, (probe.stderr or probe.stdout or "pip health check failed").strip()
    return True, "ok"


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


def _write_env_config(path: Path, values: dict[str, str]) -> None:
    lines = [f"{key}={value}" for key, value in values.items()]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _import_probe(venv_python: Path) -> tuple[bool, str]:
    probe = subprocess.run(
        [str(venv_python), "-c", "import gigaam; print('IMPORT_OK')"],
        text=True,
        capture_output=True,
    )
    ok = probe.returncode == 0 and "IMPORT_OK" in (probe.stdout or "")
    details = (probe.stderr or probe.stdout or "").strip()
    return ok, details


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap local GigaAM-v3 runtime for the public skill")
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--repo-url", default=DEFAULT_GIGAAM_REPO_URL)
    parser.add_argument("--model", default="v3_e2e_rnnt")
    parser.add_argument("--chunk-seconds", default="22")
    parser.add_argument("--ffmpeg-bin", default=shutil.which("ffmpeg") or "ffmpeg")
    parser.add_argument("--ffmpeg-mode", choices=["auto", "system", "download"], default="auto")
    parser.add_argument("--ffmpeg-url")
    parser.add_argument("--force-recreate-venv", action="store_true")
    args = parser.parse_args()

    skill_root = Path(__file__).resolve().parents[1]
    repo_root = skill_root.parent
    env_id = _detect_env_id()
    runtime_root = repo_root / ".runtime" / env_id
    venv_dir = runtime_root / "gigaam-venv"
    repo_dir = runtime_root / "GigaAM"
    config_dir = skill_root / "config"
    config_path = config_dir / f"local.{env_id}.env"
    default_config_path = config_dir / "local.env"
    env_map_path = config_dir / "environments.json"

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

    recreate_reason = None
    if args.force_recreate_venv and venv_dir.exists():
        shutil.rmtree(venv_dir)
        recreate_reason = "forced"

    if venv_dir.exists() and recreate_reason is None:
        healthy, reason = _venv_is_healthy(venv_dir)
        if not healthy:
            shutil.rmtree(venv_dir)
            recreate_reason = reason

    if not venv_dir.exists():
        run([args.python, "-m", "venv", str(venv_dir)])
        if recreate_reason is None:
            recreate_reason = "created"

    venv_python = _venv_python_path(venv_dir)
    pip_base = [str(venv_python), "-m", "pip"]
    run(pip_base + ["install", "--upgrade", "pip", "setuptools", "wheel"])
    run(pip_base + ["install", "hydra-core==1.3.*", "numpy==2.*", "omegaconf==2.3.*", "onnx==1.19.*", "onnxruntime==1.23.*", "sentencepiece", "tqdm"])
    run(pip_base + ["install", "--index-url", DEFAULT_TORCH_CPU_INDEX_URL, "torch>=2.5,<2.9", "torchaudio>=2.5,<2.9"])
    run(pip_base + ["install", "--no-deps", "-e", str(repo_dir)])

    import_ok, import_probe_details = _import_probe(venv_python)

    env_values = {
        "GIGAAM_ENV_ID": env_id,
        "GIGAAM_LOCAL_PYTHON": str(venv_python),
        "GIGAAM_MODEL": args.model,
        "GIGAAM_FFMPEG_BIN": ffmpeg_path,
        "GIGAAM_MAX_CHUNK_SECONDS": args.chunk_seconds,
        "GIGAAM_OUTPUT_ROOT": str(skill_root / "output" / "transcripts" / env_id),
    }
    _write_env_config(config_path, env_values)
    _write_env_config(default_config_path, env_values)

    env_map = {}
    if env_map_path.exists():
        try:
            env_map = json.loads(env_map_path.read_text(encoding="utf-8"))
        except Exception:
            env_map = {}
    env_map[env_id] = {
        "config_path": str(config_path),
        "runtime_root": str(runtime_root),
        "venv_python": str(venv_python),
        "ffmpeg_path": ffmpeg_path,
    }
    env_map_path.write_text(json.dumps(env_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    result = {
        "status": "ok" if import_ok else "needs-attention",
        "ready": import_ok,
        "env_id": env_id,
        "skill_root": str(skill_root),
        "repo_root": str(repo_root),
        "runtime_root": str(runtime_root),
        "repo_dir": str(repo_dir),
        "venv_python": str(venv_python),
        "config_path": str(config_path),
        "default_config_path": str(default_config_path),
        "env_map_path": str(env_map_path),
        "ffmpeg_path": ffmpeg_path,
        "ffmpeg_source": ffmpeg_source,
        "venv_recreate_reason": recreate_reason,
        "import_probe_ok": import_ok,
        "import_probe_details": import_probe_details,
        "next_step": f"Run python3 {Path(__file__).resolve().parent / 'run_gigaam_transcription.py'} --input /absolute/path/to/file --env-file {config_path}",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if import_ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
