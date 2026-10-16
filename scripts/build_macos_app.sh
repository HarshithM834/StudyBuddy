#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
if [[ "$(uname -s)" != Darwin ]]; then
  printf 'This native target must be built on macOS 14 or newer. Linux cannot validate AppKit/ScreenCaptureKit.\n' >&2
  exit 1
fi
if ! xcrun --find swiftc >/dev/null 2>&1; then
  printf 'Install the free Apple Command Line Tools with xcode-select --install, then retry.\n' >&2
  exit 1
fi
app_path="$PWD/.studybuddy/StudyBuddy.app"
mkdir -p "$app_path/Contents/MacOS" "$app_path/Contents/Resources" "$PWD/.studybuddy/swift-cache"
xcrun swiftc -swift-version 5 -O -target "$(uname -m)-apple-macosx14.0" \
  -module-cache-path "$PWD/.studybuddy/swift-cache" \
  -framework AppKit -framework WebKit -framework ScreenCaptureKit -framework Vision \
  native/macos/StudyBuddy.swift -o "$app_path/Contents/MacOS/StudyBuddy"
.venv/bin/python - "$app_path" "$PWD" <<'PY'
import plistlib
import sys
from pathlib import Path
app, source = map(Path, sys.argv[1:])
with (app / 'Contents/Info.plist').open('wb') as stream:
    plistlib.dump({
        'CFBundleExecutable': 'StudyBuddy', 'CFBundleIdentifier': 'local.studybuddy.companion',
        'CFBundleName': 'StudyBuddy', 'CFBundleDisplayName': 'StudyBuddy',
        'CFBundlePackageType': 'APPL', 'CFBundleVersion': '2',
        'CFBundleShortVersionString': '0.2.0', 'LSMinimumSystemVersion': '14.0',
        'LSUIElement': True, 'NSHighResolutionCapable': True,
        'NSAppTransportSecurity': {'NSAllowsLocalNetworking': True},
        'NSScreenCaptureUsageDescription': 'StudyBuddy reads your active study window while study mode is on to explain the material beside it.',
        'StudyBuddySourceRoot': str(source),
    }, stream)
PY
# Local ad-hoc signing is free; this is not notarized public distribution.
codesign --force --sign - "$app_path"
printf 'Built %s\nOpen with: open "%s"\nKeep the source folder in place. Rebuild after moving it.\n' "$app_path" "$app_path"
