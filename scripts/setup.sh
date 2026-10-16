#!/usr/bin/env bash
set -euo pipefail
studybuddy_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$studybuddy_root"
studybuddy_cache="${STUDYBUDDY_CACHE_DIR:-$studybuddy_root/.studybuddy/cache}"
mkdir -p "$studybuddy_cache"
studybuddy_python="${STUDYBUDDY_PYTHON:-python3}"
if ! command -v "$studybuddy_python" >/dev/null 2>&1; then
  printf 'Python was not found. See docs/mac-setup.md and set STUDYBUDDY_PYTHON.\n' >&2
  exit 1
fi
"$studybuddy_python" -c 'import sys; sys.exit("StudyBuddy needs Python 3.12 or newer. Set STUDYBUDDY_PYTHON to that executable.") if sys.version_info < (3,12) else None'
if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then
  printf 'Node and npm are required. See docs/mac-setup.md.\n' >&2
  exit 1
fi
node -e 'const [major, minor] = process.versions.node.split(".").map(Number); if (!(major === 20 && minor >= 19 || major === 22 && minor >= 12 || major > 22)) { console.error("StudyBuddy needs Node 20.19+ or 22.12+. See docs/mac-setup.md."); process.exit(1); }'
if ! command -v tesseract >/dev/null 2>&1; then
  printf 'OCR is unavailable. Install Tesseract for the Week 6/Mac acceptance session; image-only neighboring slides need it.\n' >&2
fi
"$studybuddy_python" -m venv .venv
.venv/bin/python -m pip install --cache-dir "$studybuddy_cache/pip" -r requirements.lock
npm ci --cache "$studybuddy_cache/npm" --no-audit --no-fund
npm run build
printf 'Workspace installed. Install the free local tutor with: .venv/bin/python scripts/setup_local_tutor.py\n'
printf 'Start a study session with: .venv/bin/python scripts/run.py\n'
