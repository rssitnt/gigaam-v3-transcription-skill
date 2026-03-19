#!/usr/bin/env python3
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOT = REPO_ROOT / ".runtime"
SKILL_ROOT = REPO_ROOT / "skill"
CONFIG_PATH = SKILL_ROOT / "config" / "local.env"
REPORT_PATH = REPO_ROOT / "artifacts" / "install-report.json"


def read_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def main() -> int:
    env = read_env(CONFIG_PATH)
    python_path = env.get("GIGAAM_LOCAL_PYTHON", "")
    ffmpeg_path = env.get("GIGAAM_FFMPEG_BIN", "")

    checks = {
        "repo_root_exists": REPO_ROOT.exists(),
        "runtime_root_exists": RUNTIME_ROOT.exists(),
        "gigaam_repo_exists": (RUNTIME_ROOT / "GigaAM").exists(),
        "venv_exists": (RUNTIME_ROOT / "gigaam-venv").exists(),
        "config_exists": CONFIG_PATH.exists(),
        "configured_python_exists": bool(python_path) and Path(python_path).exists(),
        "configured_ffmpeg_exists": bool(ffmpeg_path) and (Path(ffmpeg_path).exists() or shutil.which(ffmpeg_path) is not None),
    }

    probe_ok = False
    probe_stdout = ""
    probe_stderr = ""
    if checks["configured_python_exists"]:
        runtime_script = SKILL_ROOT / "scripts" / "gigaam_skill_runtime.py"
        probe_output = REPO_ROOT / "artifacts" / "probe-report.json"
        command = [python_path, str(runtime_script), "probe", "--probe-output", str(probe_output)]
        completed = subprocess.run(command, capture_output=True, text=True)
        probe_ok = completed.returncode == 0
        probe_stdout = completed.stdout
        probe_stderr = completed.stderr
        checks["runtime_probe_ok"] = probe_ok
    else:
        checks["runtime_probe_ok"] = False

    ready = all(checks.values())
    payload = {
        "status": "ok" if ready else "needs-attention",
        "ready": ready,
        "repo_root": str(REPO_ROOT),
        "skill_root": str(SKILL_ROOT),
        "runtime_root": str(RUNTIME_ROOT),
        "config_path": str(CONFIG_PATH),
        "checks": checks,
        "next_command": f"python3 {SKILL_ROOT / 'scripts' / 'run_gigaam_transcription.py'} --input /absolute/path/to/file --env-file {CONFIG_PATH}",
        "probe_stdout": probe_stdout,
        "probe_stderr": probe_stderr,
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if ready else 2


if __name__ == "__main__":
    raise SystemExit(main())
