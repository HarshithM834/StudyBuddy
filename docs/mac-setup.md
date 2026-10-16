# Install StudyBuddy’s local engine on a Mac

For the primary menu-bar app, follow [Mac companion setup](mac-companion.md). This page covers shared prerequisites and the supporting browser workspace for development.

The selected model is Qwen3.5-4B, with an Unsloth Q4_K_M quantization and F16 vision projector. Its model/quantization revisions and provenance are pinned in the installer. The installer selects an official llama.cpp build for Apple silicon or Intel and checks its published SHA-256. The selected model weights have an Apache-2.0 declaration. No inference account or API key is required.

The founder's target is an M3 Pro Mac with 18 GB memory (OS version reported as "Golden Gate 27.0"). Mac execution has not been verified in this Linux cloud environment. Memory and speed need checking on the actual Mac. The startup script requests GPU offload on Apple silicon using the runtime's Metal backend. The model files occupy about 3.4 GB; allow at least 8 GB of free disk for model files, runtime, dependencies, and course material. The expanded Linux screen ended at roughly 10.2 GB of model process memory; that is a measurement on Linux, not a Mac minimum-memory guarantee. Apple silicon acceleration may improve performance, but it has not been measured here.

## Prerequisites

Install Git, Node 22.12 or newer, Python 3.12 or newer, and Tesseract with English OCR data for the Week 6 acceptance session. OCR lets the tutor read neighboring image-only slides; text-only PDFs can still be used without it. If Homebrew is already installed:

```bash
brew install node@22 python@3.12 tesseract
export PATH="$(brew --prefix node@22)/bin:$PATH"
export STUDYBUDDY_PYTHON="$(brew --prefix python@3.12)/bin/python3.12"
```

Homebrew and these tools are free and open source. If using another installation method, set `STUDYBUDDY_PYTHON` to the correct Python executable and make sure Node is on `PATH`.

## Install from GitHub or the source bundle

Clone the repository, or use the prepared StudyBuddy source directory. Do not copy a Linux `.venv` or runtime onto the Mac. Preserve `.studybuddy/` when updating an existing installation.

```bash
git clone https://github.com/HarshithM834/StudyBuddy.git
cd StudyBuddy
```

From the StudyBuddy directory:

```bash
bash scripts/setup.sh
.venv/bin/python scripts/setup_local_tutor.py
```

The first model download is about 3.4 GB. Later runs verify and reuse it.

## Start the supporting workspace for development

Start the workspace and tutor together:

```bash
.venv/bin/python scripts/run.py
```

On macOS this opens your default browser when the app and tutor are ready. `bash StudyBuddy.command` now opens the native menu-bar app on macOS; it is not the browser launcher. The app uses loopback port 8000 and the tutor uses port 8081. Type `localhost:8000` into the Mac browser if it does not open automatically. This is a local session on your Mac, not a hosted preview.

Control-C stops processes started by this launcher and keeps saved work. If a healthy tutor was already running, the launcher reuses it and leaves it running. A port conflict produces a clear error instead of stopping another process. Startup logs are in `.studybuddy/logs/`; the last session's startup times are recorded there. To open only PDFs and notes, use `.venv/bin/python scripts/run.py --workspace-only`.

For separate development terminals, the original commands still work: `.venv/bin/python scripts/start_local_tutor.py` and `bash scripts/start.sh`.

The tutor is still experimental: initial live checks found incorrect feedback and unsupported claims. Use this build to test the workflow and record failures; it is not yet the finished MVP. See `docs/validation.md` and `docs/mvp-release-plan.md`.

Slides, notes, conversations, and model files remain in `.studybuddy/`. Keep that directory when updating the source. The uploaded class presentation is not bundled in the Git repository.

If startup reports missing files, rerun the installer. If the model cannot fit in memory or answers are too slow, record the chip, memory, error message, and response time so the local model settings can be adjusted. Do not substitute a paid service.

## Complete the Mac check

Follow the [founder acceptance session](mac-acceptance.md) for the full PDF → tutor → quiz → saved work → restart → offline journey. Run `.venv/bin/python scripts/diagnose.py` if setup fails; it prints model/platform/health information without reading course notes or credentials.

The [evaluation guide](../evaluations/README.md) provides the frozen 20-case quality screen, three trials of critical regressions, and the 30-response timing sample. Evaluations use isolated temporary storage and check the original deck fingerprint. They leave your saved study work untouched. Successful HTTP requests are not a quality pass: a human must review the answers and cited pages.
