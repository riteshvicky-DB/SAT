#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Starting backend on http://localhost:8000"
(
  cd "$ROOT_DIR/backend"
  if [ ! -d ".venv" ]; then
    python -m venv .venv
  fi
  source .venv/bin/activate
  pip install -r requirements.txt
  python scripts/seed.py
  uvicorn app.main:app --host 0.0.0.0 --port 8000
) &

echo "Starting frontend on http://localhost:5173"
(
  cd "$ROOT_DIR/frontend"
  npm install
  npm run dev
)
