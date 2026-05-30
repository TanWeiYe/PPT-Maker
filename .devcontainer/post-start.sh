#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

LOG_DIR="$REPO_ROOT/.devcontainer/.logs"
mkdir -p "$LOG_DIR"
BACKEND_LOG="$LOG_DIR/backend.log"
FRONTEND_LOG="$LOG_DIR/frontend.log"
BACKEND_ENTRY="${BACKEND_ENTRY:-web/app.py}"
BACKEND_STARTED=0
FRONTEND_STARTED=0
HAS_LSOF=0

if command -v lsof >/dev/null 2>&1; then
  HAS_LSOF=1
fi

FRONTEND_DIR=""
for dir in frontend client web; do
  if [ -f "$dir/package.json" ]; then
    if grep -q '"vue"' "$dir/package.json"; then
      FRONTEND_DIR="$dir"
      break
    fi
  fi
done

if [ ! -f "$BACKEND_ENTRY" ]; then
  echo "[devcontainer] Backend entry '$BACKEND_ENTRY' not found; skipping backend start. Set BACKEND_ENTRY to the correct app file if needed."
elif { [ "$HAS_LSOF" -eq 1 ] && ! lsof -ti:5000 >/dev/null 2>&1; } || { [ "$HAS_LSOF" -eq 0 ] && ! pgrep -f "python3.*$(basename "$BACKEND_ENTRY")" >/dev/null 2>&1; }; then
  echo "[devcontainer] Starting Python backend ($BACKEND_ENTRY) on port 5000..."
  : > "$BACKEND_LOG"
  nohup env PORT=5000 python3 "$BACKEND_ENTRY" > "$BACKEND_LOG" 2>&1 &
  BACKEND_STARTED=1
else
  echo "[devcontainer] Port 5000 already in use; skipping backend start."
fi

if [ -n "$FRONTEND_DIR" ]; then
  if ! grep -q '"dev"[[:space:]]*:' "$FRONTEND_DIR/package.json"; then
    echo "[devcontainer] No 'dev' script found in $FRONTEND_DIR/package.json; skipping frontend start."
  elif { [ "$HAS_LSOF" -eq 1 ] && ! lsof -ti:5173 >/dev/null 2>&1; } || { [ "$HAS_LSOF" -eq 0 ] && ! pgrep -f "(vite|npm run dev|vue-cli-service serve)" >/dev/null 2>&1; }; then
    echo "[devcontainer] Starting Vue frontend from '$FRONTEND_DIR' on port 5173..."
    (
      cd "$FRONTEND_DIR"
      : > "$FRONTEND_LOG"
      nohup npm run dev -- --host 0.0.0.0 --port 5173 > "$FRONTEND_LOG" 2>&1 &
    )
    FRONTEND_STARTED=1
  else
    echo "[devcontainer] Port 5173 already in use; skipping frontend start."
  fi
else
  echo "[devcontainer] No Vue frontend detected; skipping frontend start."
fi

if [ "$BACKEND_STARTED" -eq 1 ] && [ "$FRONTEND_STARTED" -eq 1 ]; then
  echo "[devcontainer] Active logs: $BACKEND_LOG and $FRONTEND_LOG"
elif [ "$BACKEND_STARTED" -eq 1 ]; then
  echo "[devcontainer] Active logs: $BACKEND_LOG"
elif [ "$FRONTEND_STARTED" -eq 1 ]; then
  echo "[devcontainer] Active logs: $FRONTEND_LOG"
else
  echo "[devcontainer] No new services started in this session."
fi
