#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${1:-}"
TARGET_DIR="${2:-}"

if [[ -z "$REPO_URL" ]]; then
  echo "Usage: bash ./scripts/install-from-url.sh <repo-url> [target-dir]" >&2
  exit 2
fi

if ! command -v git >/dev/null 2>&1; then
  echo "git не найден. Установи git и повтори запуск." >&2
  exit 2
fi

if [[ -z "$TARGET_DIR" ]]; then
  name="$(basename "$REPO_URL")"
  TARGET_DIR="${name%.git}"
fi

if [[ ! -d "$TARGET_DIR" ]]; then
  git clone "$REPO_URL" "$TARGET_DIR"
fi

cd "$TARGET_DIR"
bash ./scripts/install.sh
python3 ./scripts/verify_install.py
