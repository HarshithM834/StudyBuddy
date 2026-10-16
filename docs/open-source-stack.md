# Open-source stack and costs

The user's constraint is free resources and open-source software only. The implemented workflow uses local storage and local inference, with no hosted inference adapter. The API rejects model endpoints outside loopback. This avoids license subscriptions and per-question API fees; running the app still requires hardware and electricity. Cloud hosting is not assumed to be free.

GitHub repository search and upstream source/license inspection were performed on October 14, 2026. Adding every available library would increase maintenance. The implementation uses the smaller set needed for the current workflow.

| Project | Role | License / decision |
| --- | --- | --- |
| [React](https://github.com/facebook/react) | Study workspace UI | MIT |
| [Vite](https://github.com/vitejs/vite) | Local development and production build | MIT |
| [FastAPI](https://github.com/fastapi/fastapi) | Local application API | MIT |
| [pypdfium2](https://github.com/pypdfium2-team/pypdfium2) | PDF rendering and text extraction | Apache-2.0 / BSD-3-Clause; PDFium and dependency notices also apply |
| [Tesseract](https://github.com/tesseract-ocr/tesseract) | Local OCR fallback | Apache-2.0; optional system dependency |
| [llama.cpp](https://github.com/ggml-org/llama.cpp) | CPU-capable local model server | MIT; selected runtime, release `b11429` |
| [Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B) | Experimental local vision-language tutor | Apache-2.0; pinned [Unsloth Q4_K_M quantization](https://huggingface.co/unsloth/Qwen3.5-4B-GGUF), official upstream license/cards retained. Earlier Qwen3-VL-4B remains a measured baseline |
| [Ollama](https://github.com/ollama/ollama) | Alternative local runtime investigated | MIT; not required or installed |
| [pypdf](https://github.com/py-pdf/pypdf) | PDF parsing alternative investigated | BSD-3-Clause; not a project dependency |
| [Lucide](https://github.com/lucide-icons/lucide) | Interface icons | ISC |
| [react-markdown](https://github.com/remarkjs/react-markdown) | Render tutor answers without raw HTML | MIT |

SQLite is bundled with Python and is in the public domain. Uploaded files, model weights, caches, and the SQLite database live in ignored local storage. The UI has no external font service or analytics SDK.

An initial development draft used PyMuPDF. Its [AGPL license](https://github.com/pymupdf/PyMuPDF/blob/main/COPYING) was inspected and the application dependency was replaced with PDFium to keep the selected application stack permissively licensed. Earlier one-off research renders are not runtime dependencies.

Upstream attribution and license obligations still apply. Runtime archive notices remain with the extracted binary; the model installer retains its license and model card. Dependency license files are distributed by their installed packages. This list is an engineering record, not a legal opinion about every future deployment.

## Current product boundaries

- The implemented app is a personal PDF workspace. It has no accounts, billing, lecture recording, Drive/Outlook integration, or operating-system overlay.
- The guided Hamming lab is deterministic. It does not pretend to be an AI response.
- Live responses require a running local model. The app shows an offline state when it is unavailable.
- The models run within the cloud machine's memory. Both the earlier Qwen3-VL model and the expanded Qwen3.5-4B screen exposed critical answer-quality failures. Mac performance remains unmeasured; see `docs/validation.md`.
- Source links are constrained to pages provided to the model. They are not proof that every model claim is correct.
- General concept diagrams persist with their originating assistant message. Manual highlights and pins persist independently.
- The current proof point is that the workflow functions. Student preference, retention, and willingness to pay remain untested.

## Native Mac companion (October 16)

The source shell uses Swift with AppKit, WebKit, ScreenCaptureKit and Vision supplied by macOS; these are Apple platform APIs, not open-source third-party libraries. They require no additional service payment or Developer Program membership for the local source-built alpha. The build uses free Command Line Tools and local ad-hoc signing. React/FastAPI/SQLite and the existing open-source local model runtime remain the application engine. No Electron/Tauri package, browser extension, commercial screen API, telemetry service, or paid fallback was added. Actual Mac build/capture remains unverified.
