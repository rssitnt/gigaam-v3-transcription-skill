#!/usr/bin/env bash
set -euo pipefail

PYTHON_CMD="${PYTHON_CMD:-}"
FFMPEG_MODE="${FFMPEG_MODE:-auto}"

resolve_python() {
  if [[ -n "$PYTHON_CMD" ]] && command -v "$PYTHON_CMD" >/dev/null 2>&1; then
    echo "$PYTHON_CMD"
    return 0
  fi
  for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1; then
      echo "$candidate"
      return 0
    fi
  done
  return 1
}

install_python_linux() {
  if command -v apt-get >/dev/null 2>&1; then
    echo "Python не найден. Пытаюсь установить через apt-get..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-venv python3-pip
    return 0
  fi
  if command -v dnf >/dev/null 2>&1; then
    echo "Python не найден. Пытаюсь установить через dnf..."
    sudo dnf install -y python3 python3-pip
    return 0
  fi
  if command -v pacman >/dev/null 2>&1; then
    echo "Python не найден. Пытаюсь установить через pacman..."
    sudo pacman -Sy --noconfirm python python-pip
    return 0
  fi
  echo "Не удалось автоматически установить Python: не найден поддерживаемый пакетный менеджер." >&2
  return 1
}

if ! PY=$(resolve_python); then
  install_python_linux
  PY=$(resolve_python)
fi

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BOOTSTRAP="$REPO_ROOT/skill/scripts/bootstrap_gigaam_runtime.py"

echo "Использую Python: $PY"
"$PY" "$BOOTSTRAP" --ffmpeg-mode "$FFMPEG_MODE"
