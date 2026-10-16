#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if [[ ! -x .venv/bin/python ]]; then
  printf 'Open Terminal in this folder and run: bash scripts/setup.sh\n'
  exit 1
fi
if [[ "$(uname -s)" == Darwin ]]; then
  if [[ ! -d .studybuddy/StudyBuddy.app ]]; then bash scripts/build_macos_app.sh; fi
  exec open .studybuddy/StudyBuddy.app
fi
exec .venv/bin/python scripts/run.py --no-browser
