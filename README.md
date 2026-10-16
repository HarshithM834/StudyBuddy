# StudyBuddy — Mac study companion

The primary product is a Mac menu-bar app with a floating tutor that follows your active study window across Canvas, YouTube, PowerPoint, and other apps while study mode is on. The local PDF workspace below provides course material and saved work. The native integration is an alpha: source is written, but macOS compilation/capture and tutor correctness remain unverified.

Start with [Mac companion setup](docs/mac-companion.md), the [product baseline](docs/product/README.md), and the [validation record](docs/validation.md).

## Supporting workspace

A personal study workspace with your lecture on one side and a tutor and saved notes on the other. The tutor runs locally using open-source software and Apache-2.0 model weights, with no API key or per-request charge. Inference endpoints are restricted to loopback; there is no hosted-provider adapter.

**Current status:** the PDF workspace and local inference run. Initial real-model checks exposed incorrect feedback and unsupported claims; the tutor has not passed the MVP release gate. See [validation](docs/validation.md). The target is an M3 Pro Mac with 18 GB memory, where execution and performance still need checking.

## Product direction and scope

Start with the [product baseline](docs/product/README.md): the vision, PRD, MRD, competitive analysis, and visual roadmap. The PRD is the source of truth for release requirements; the roadmap sets sequence and conditional dates. Implementation work should map to those documents, with new ideas recorded before they enter the release scope.

## What works

- Import PDFs, browse slide thumbnails, search slide titles, and resume the last viewed slide.
- Highlight slide regions and attach pinned notes. Coordinates scale with the slide.
- Save notes, annotations, and conversations separately for each slide in SQLite.
- Export a slide's notes as Markdown.
- Ask the tutor for an explanation, a concept diagram, or an application question; responses include source-slide links.
- Use the deterministic Hamming visual lab on the supplied CYSE 425 Week 6 deck.

The live tutor requires a local model server. The app displays its actual connection state. The Hamming lab uses fixed, verified logic and is labeled as a guided example.

## Install and start the supporting workspace

Prerequisites: Python 3.12+, Node 20.19+ (or 22.12+), and npm. Tesseract with English data is optional for OCR of image-only slides. The supplied cloud machine already has it.

```bash
bash scripts/setup.sh
bash scripts/start.sh
```

The app binds to loopback port 8000. Use `STUDYBUDDY_PORT` to choose another port. This is a personal development app; it has no account authentication and should remain on a trusted local machine.

Import a lecture using the upload button. To restore the supplied deck in this cloud checkout:

```bash
.venv/bin/python scripts/import_lecture.py \
  '/workspace/attachments/b18a0452-1122-47a0-ae01-b014d972b824/CYSE 425 Week 6.pdf' \
  --course 'CYSE 425' --week6
```

The upload and application data are stored in ignored `.studybuddy/`; they are not committed. This cloud instance already has the 44-slide deck imported. A fresh Git clone needs the user to supply their PDF.

## Free local tutor

The included installer selects the Linux x86-64, macOS Apple silicon, or macOS Intel llama.cpp release and verifies its published SHA-256. It checks the model's Apache-2.0 license metadata, pins the resolved repository revision, and verifies downloaded GGUF weights against the Hugging Face LFS SHA-256 values. The installer retains both the quantizer’s and official base model’s cards, plus the pinned upstream Apache-2.0 license text and provenance.

```bash
.venv/bin/python scripts/setup_local_tutor.py
.venv/bin/python scripts/start_local_tutor.py
```

For the supporting browser workspace, start both services with `.venv/bin/python scripts/run.py` (add `--no-browser` in cloud tasks). This opens the browser on macOS and stops only its own processes on Control-C. The model listens on loopback port 8081. The selected candidate is `unsloth/Qwen3.5-4B-GGUF`, based on the official Apache-2.0 `Qwen/Qwen3.5-4B`, using pinned Q4_K_M weights and the F16 projector, approximately 3.4 GB of model downloads. CPU inference is supported; speed depends on the machine. The startup script defaults to four CPU threads, an 8,192-token context and a 1,024 MiB prompt-cache limit. The installed profile is still experimental; see the latest validation record for model/reasoning quality results.

Required download hosts include `github.com`, `release-assets.githubusercontent.com`, `huggingface.co`, and the actual Hugging Face CDN redirect, currently `us.aws.cdn.hf.co`. A proxy denial requires the environment's network policy to be applied; an API key does not fix it. Do not disable TLS or checksum verification.

The model and runtime are retained on disk. Their processes must be restarted in a new task. Existing valid downloads are reused.

For Mac prerequisites and the first run, see [Mac setup](docs/mac-setup.md). Mac execution and performance still require testing on the user's machine.

Local mode reads the current slide image, nearby text, relevant excerpts, and the slide's recent conversation. Optional OCR supplements image-only pages. OCR and model interpretations can be wrong, especially for equations; source links support checking answers. Learning improvement and tutoring accuracy have not been established by application tests.

Optional settings:

| Variable | Default / purpose |
| --- | --- |
| `STUDYBUDDY_LOCAL_URL` | Local model server on loopback port 8081; remote endpoints are rejected |
| `STUDYBUDDY_THREADS` | `4` |
| `STUDYBUDDY_TUTOR_TIMEOUT` | `240` seconds; allowed range 30–600 for deliberate CPU evaluation |
| `STUDYBUDDY_DATA_DIR` | `.studybuddy` under the checkout |
| `STUDYBUDDY_LLAMA_SERVER` | Override the installed llama-server executable |
| `STUDYBUDDY_LOCAL_MODEL` | Override the model file |
| `STUDYBUDDY_LOCAL_PROJECTOR` | Override the vision projector file |
| `STUDYBUDDY_LOCAL_VISION` | `1`; set `0` when deliberately using a text-only local model |

Legacy `STUDYBUDDY_PROVIDER`, `STUDYBUDDY_API_KEY`, and `STUDYBUDDY_MODEL` settings are unused. An obsolete API-key requirement may still appear in the cloud environment draft; remove it in environment settings rather than supplying a key. The draft-editing tool cannot remove existing credential requirements.

## Development and validation

```bash
# Backend; serves the production build if it exists
.venv/bin/python -m uvicorn server.app:app --host 127.0.0.1 --port 8000 --reload

# Separate terminal: frontend hot reload, with /api proxied to the backend
npm run dev

# Type check + production build
npm run build

# API tests; use temporary databases and mocked model responses
.venv/bin/python -m unittest discover -s tests -v
```

The tests verify PDF handling, state isolation/persistence, annotation validation, source/visual persistence, remote-endpoint rejection, and local-only inference despite legacy provider settings. Mocked model responses do not validate a real model or educational quality. The [frozen local-model screen](evaluations/README.md) and [Mac acceptance journey](docs/mac-acceptance.md) cover the remaining release checks. See [the validation record](docs/validation.md) for measured results and [the release plan](docs/mvp-release-plan.md) for this week's scope.

Use the existing checkout in cloud tasks; each task is already isolated. No additional Git worktree is needed.

## Open-source choices

See [the resource and cost notes](docs/open-source-stack.md) for upstream projects, licenses, and current limitations. Notes about the first user problem and the Hamming lesson are in [the Week 6 pilot](docs/week6-pilot.md).
