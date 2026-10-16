"""Run the local tutor in the foreground. Stop it with Ctrl-C."""
import json
import os
import platform
from pathlib import Path

root = Path(__file__).resolve().parents[1]
data = Path(os.environ.get("STUDYBUDDY_DATA_DIR", root / ".studybuddy"))
runtime_record = data / "runtime" / "b11429" / "verified-runtime.json"
model_record = data / "models" / "model.json"
binary = os.environ.get("STUDYBUDDY_LLAMA_SERVER")
if not binary and runtime_record.exists():
    binary = json.loads(runtime_record.read_text())["executable"]
model = os.environ.get("STUDYBUDDY_LOCAL_MODEL")
projector = os.environ.get("STUDYBUDDY_LOCAL_PROJECTOR")
metadata = {}
if not model and model_record.exists():
    metadata = json.loads(model_record.read_text())
    model = str(data / "models" / metadata["filename"])
    if not projector and metadata.get("projector"):
        projector = str(data / "models" / metadata["projector"])
if not binary or not model or not Path(binary).exists() or not Path(model).exists():
    raise SystemExit("Local tutor files are missing. Run: python3 scripts/setup_local_tutor.py")
threads = os.environ.get("STUDYBUDDY_THREADS", "4")
args = [binary, "-m", model, "--host", "127.0.0.1", "--port", "8081", "-c", "8192", "-t", threads, "-tb", threads, "--parallel", "1", "--cache-ram", "1024", "--jinja", "--no-webui"]
if metadata.get("chat_template_kwargs"):
    args.extend(["--chat-template-kwargs", json.dumps(metadata["chat_template_kwargs"])])
if metadata.get("reasoning"):
    args.extend(["--reasoning", metadata["reasoning"]])
if platform.system() == "Darwin" and platform.machine() == "arm64":
    args.extend(["--n-gpu-layers", "99"])
if projector:
    args.extend(["--mmproj", projector])
os.execv(binary, args)
