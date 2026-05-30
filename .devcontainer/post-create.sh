#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

FRONTEND_DIR=""
for dir in frontend client web; do
  if [ -f "$dir/package.json" ]; then
    if grep -q '"vue"' "$dir/package.json"; then
      FRONTEND_DIR="$dir"
      break
    fi
  fi
done

echo "[devcontainer] Installing FFmpeg..."
sudo apt-get update
if ! sudo apt-get install -y ffmpeg lsof; then
  echo "[devcontainer] FFmpeg/lsof installation failed. Check network connectivity or Codespaces logs for details." >&2
  exit 1
fi

echo "[devcontainer] Installing Python dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

if [ -f ".env.example" ] && [ ! -f ".env" ]; then
  echo "[devcontainer] Initializing backend .env from .env.example"
  cp .env.example .env
fi

mkdir -p web/runtime

if [ -n "$FRONTEND_DIR" ]; then
  echo "[devcontainer] Detected Vue frontend at '$FRONTEND_DIR', installing Node dependencies..."
  (
    cd "$FRONTEND_DIR"
    if [ -f package-lock.json ]; then
      if ! npm ci; then
        echo "[devcontainer] npm ci failed in $FRONTEND_DIR. Common causes: lockfile mismatch, network issues, or incompatible Node version." >&2
        exit 1
      fi
    else
      if ! npm install; then
        echo "[devcontainer] npm install failed in $FRONTEND_DIR. Common causes: network issues, missing system deps, or incompatible Node version." >&2
        exit 1
      fi
    fi
    if [ -f .env.example ] && [ ! -f .env ]; then
      echo "[devcontainer] Initializing frontend .env from .env.example"
      cp .env.example .env
    fi
  )
else
  echo "[devcontainer] No Vue frontend package.json detected in frontend/, client/, or web/; skipping Node dependency install."
fi

echo "[devcontainer] Setup complete."
