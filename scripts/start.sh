#!/usr/bin/env bash
set -euo pipefail
studybuddy_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$studybuddy_root"
if [[ ! -f dist/index.html || ! -x .venv/bin/python ]]; then
  printf 'Run bash scripts/setup.sh first.\n' >&2
  exit 1
fi
exec .venv/bin/python -m uvicorn server.app:app --host 127.0.0.1 --port "${STUDYBUDDY_PORT:-8000}"
