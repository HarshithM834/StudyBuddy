# Mac menu-bar companion alpha

The primary StudyBuddy experience is a floating companion launched from the Mac menu bar. Turn on study mode once and it follows the active ordinary window as you switch between Canvas, YouTube, PowerPoint, Preview, or another app. There is no app/window selector. The code is implemented; actual macOS compilation, permissions, capture compatibility and performance have not been tested in this Linux environment. This is a **source alpha**, not a finished native binary or a released MVP.

## Build on your Mac

Target: M3 Pro, 18 GB; macOS 14 or newer. Confirm the actual macOS version in About This Mac. Use a checkout containing the companion alpha; see the clone instructions in [Mac setup](mac-setup.md).

1. Install the free Apple Command Line Tools if absent: `xcode-select --install`.
2. Follow the prerequisites in [Mac setup](mac-setup.md): Python 3.12+, Node 22.12+, and Tesseract English OCR for image-only course slides.
3. In the StudyBuddy source folder, run:

```bash
bash scripts/setup.sh
.venv/bin/python scripts/setup_local_tutor.py
bash scripts/build_macos_app.sh
open .studybuddy/StudyBuddy.app
```

The model installer currently defaults to the experimental Qwen3.5-4B profile. Both 4B and 9B comparisons have open quality failures; the larger reasoning experiment is not an accepted release configuration. Do not interpret model installation as correct tutoring. No API key or paid fallback is used.

Later, double-click `StudyBuddy.command` or run `bash StudyBuddy.command`. On Mac this opens the native app. Rebuild with `bash scripts/build_macos_app.sh` after changing native source or moving the source folder. Keep the source folder and its `.studybuddy/` data in place: this alpha uses their absolute path and Python environment. It is not a standalone distributable app.

The build uses local ad-hoc signing, with no paid Apple Developer Program or notarization. It uses the AppKit, WebKit, ScreenCaptureKit and Vision APIs supplied by macOS. Those Apple frameworks are proprietary platform APIs available without an additional fee; the local inference/web stack uses the open-source components in [the stack record](open-source-stack.md). No extra commercial wrapper dependency is needed.

## Use study mode

- Click the book icon in the menu bar to show the movable, resizable companion. It floats above normal windows and requests visibility with full-screen apps; full-screen/Spaces behavior needs Mac validation.
- Click **Turn on study mode**. macOS may request Screen Recording access. Allow StudyBuddy under System Settings → Privacy & Security → Screen Recording (wording varies by macOS), then reopen the app if macOS requests it. There is no audio recording in this build.
- Study in your usual app. About every three seconds, StudyBuddy captures that app's frontmost ordinary window and reads visible text locally. It keeps the prior study window when you type in the companion itself. No whole-desktop capture or app control is implemented.
- Ask about what is visible, request a visual, or try a quiz. A request uses the snapshot available when you asked. Visible YouTube frames/captions are not a complete video transcript; the model is instructed to admit that spoken/off-screen content is unavailable. Screen reading cannot guarantee understanding or correct explanations.
- Optionally add the lecture PDF under **Course material**. This is a source attachment, not a choice of which app to follow. Preparing image-only PDFs can take time because OCR runs locally. After two matching observations, a recognized PDF slide restores its saved conversation, diagrams and notes. Uncertain matches stay in visible-screen mode.
- **Explain as I go** currently applies to recognized PDF slides. It waits for a stable slide, reuses saved conversations, and avoids a backlog while the model is busy. Automatic explanations for arbitrary app content and video audio remain open work.
- **Pause**, hiding the panel, closing it, or quitting stops capture and drops pending frame results. An already-submitted answer may finish and be saved to its original context; it is not relabeled as an answer about a newer screen. Reopening does not silently turn screen capture on.
- Right-click the menu-bar icon to quit. It stops the launcher and services it owns; a separately running model stays running. No launch-at-login registration is made.

## Data and limits

Raw screen images and OCR are held in memory and sent only to the local API/model for the requested explanation. They are not saved as a screen-recording archive. Completed questions and answers are saved locally in `.studybuddy/studybuddy.sqlite3` and can contain material from the screen. Course PDFs and their OCR caches are retained locally as before. No analytics or remote inference are added.

Known PDF pages have stable document/page identities. Other contexts currently use application, window title and normalized visible text, with an image fingerprint for views with little text. Zoom, OCR differences, changing captions or renamed windows can create a new context. Visually different pages with the same extracted text may share a context; this needs further testing. Broad cross-app memory is not yet reliable enough to call finished.

Protected video, minimized windows, diagrams with little readable text, multiple visible slides, permissions, and macOS version differences may prevent useful capture or matching. App/window capture compatibility must be checked on the actual Mac. The local tutor still has correctness and latency failures; see [validation](validation.md). Drawing directly on another app's slide and audio/transcript ingestion are not implemented.

## Diagnose and validate

The native app's startup log is `.studybuddy/logs/native.log`; backend/model logs are alongside it. Close an earlier development session if port 8000 is occupied. Run `.venv/bin/python scripts/diagnose.py` for curated health/model/platform information. Preserve `.studybuddy/` when updating.

Use [Mac acceptance](mac-acceptance.md) to test the actual integration. For Linux development, `npm run build` and `.venv/bin/python -m unittest discover -s tests -v` exercise the shared code. The native shell cannot be compiled or run with AppKit on Linux; a passing browser simulation does not close that gate.

Optional browser integration check (Playwright is a free test tool, not a runtime dependency): start an isolated API with `STUDYBUDDY_DATA_DIR=/tmp/studybuddy-companion-check .venv/bin/python -m uvicorn server.app:app --host 127.0.0.1 --port 8004`, then run `python3 tests/companion_browser.py` in a Python environment with Playwright and Chromium installed. It mocks native capture and inference, keeps screenshot artifacts in ignored `.studybuddy/checks/`, and does not exercise native macOS APIs.
