"""Install a checksum-verified llama.cpp runtime and a public Apache-2.0 model.

This never purchases access, supplies credentials, or calls a paid inference API.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import tarfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get("STUDYBUDDY_DATA_DIR", ROOT / ".studybuddy"))
RUNTIME_ASSETS = {
    ("Linux", "x86_64"): ("ubuntu-x64", "f6d25dde8f51133143d1453da4fd5f73b145127177612a283bf7995957af3392"),
    ("Darwin", "arm64"): ("macos-arm64", "740288ec6887be94280a5dfa25b5e23a78285cab104519e6c7e218904ee82459"),
    ("Darwin", "x86_64"): ("macos-x64", "29ac3ea02be6bd143e824973f2cc5fa74bc4094393a9eaab0ff6814f19dd8522"),
}
MODEL_PROFILES = {
    "qwen35-4b": ("unsloth/Qwen3.5-4B-GGUF", "e87f176479d0855a907a41277aca2f8ee7a09523",
                  "Qwen/Qwen3.5-4B", "851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a"),
    "qwen35-9b": ("unsloth/Qwen3.5-9B-GGUF", "3885219b6810b007914f3a7950a8d1b469d598a5",
                  "Qwen/Qwen3.5-9B", "c202236235762e1c871ad0ccb60c8ee5ba337b9a"),
}
DEFAULT_MODEL = "qwen35-4b"  # Experimental; see docs/validation.md before release.



def sha256(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(url: str, target: Path, expected: str):
    if target.exists() and sha256(target) == expected:
        print(f"Verified existing {target.name}.", flush=True)
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".partial")
    try:
        print(f"Downloading {target.name} from {urllib.parse.urlsplit(url).hostname}…", flush=True)
        digest = hashlib.sha256()
        with urllib.request.urlopen(url, timeout=60) as response, temporary.open("wb") as output:
            for chunk in iter(lambda: response.read(4 * 1024 * 1024), b""):
                output.write(chunk)
                digest.update(chunk)
        if digest.hexdigest() != expected:
            raise RuntimeError(f"Checksum verification failed for {target.name}; artifact will not be used.")
        temporary.replace(target)
        print(f"SHA-256 verified: {target.name}.", flush=True)
    finally:
        temporary.unlink(missing_ok=True)


def setup_runtime():
    target_platform = (platform.system(), "x86_64" if platform.machine() == "AMD64" else platform.machine())
    if target_platform not in RUNTIME_ASSETS:
        raise RuntimeError("This installer supports Linux x86-64 and macOS (Apple silicon or Intel). Install llama.cpp for other platforms and set STUDYBUDDY_LLAMA_SERVER to its llama-server executable.")
    asset, expected = RUNTIME_ASSETS[target_platform]
    archive_name = f"llama-b11429-bin-{asset}.tar.gz"
    runtime_url = f"https://github.com/ggml-org/llama.cpp/releases/download/b11429/{archive_name}"
    runtime = DATA / "runtime" / "b11429"
    record = runtime / "verified-runtime.json"
    if record.exists():
        metadata = json.loads(record.read_text())
        binary = Path(metadata["executable"])
        if tuple(metadata.get("platform", ["Linux", "x86_64"])) == target_platform and binary.exists() and sha256(binary) == metadata["executable_sha256"]:
            print("Local inference runtime is already installed.", flush=True)
            return binary
    archive = DATA / "downloads" / archive_name
    download(runtime_url, archive, expected)
    runtime.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "r:gz") as package:
        package.extractall(runtime, filter="data")
    candidates = list(runtime.rglob("llama-server"))
    if len(candidates) != 1:
        raise RuntimeError("The verified archive does not contain one unambiguous llama-server executable.")
    binary = candidates[0]
    record.write_text(json.dumps({"url": runtime_url, "archive_sha256": expected, "platform": list(target_platform), "executable": str(binary), "executable_sha256": sha256(binary)}, indent=2))
    return binary


def activate_model(model_dir: Path, metadata: dict):
    active = dict(metadata)
    for key in ["filename", "projector"]:
        active[key] = str((model_dir / metadata[key]).relative_to(DATA / "models"))
    temporary = DATA / "models" / "model.json.partial"
    temporary.write_text(json.dumps(active, indent=2))
    temporary.replace(DATA / "models" / "model.json")


def setup_model(profile: str = DEFAULT_MODEL):
    MODEL_REPOSITORY, MODEL_REVISION, BASE_REPOSITORY, BASE_REVISION = MODEL_PROFILES[profile]
    model_dir = DATA / "models" / profile
    record = model_dir / "model.json"
    if record.exists():
        metadata = json.loads(record.read_text())
        file = model_dir / metadata["filename"]
        projector = model_dir / metadata.get("projector", "missing")
        if (metadata.get("repository") == MODEL_REPOSITORY and metadata.get("revision") == MODEL_REVISION
                and file.exists() and sha256(file) == metadata["sha256"]
                and projector.is_file() and sha256(projector) == metadata.get("projector_sha256")
                and (model_dir / "LICENSE-model").is_file()
                and sha256(model_dir / "LICENSE-model") == metadata.get("license_sha256")
                and (model_dir / "MODEL-CARD.md").is_file() and (model_dir / "BASE-MODEL-CARD.md").is_file()):
            activate_model(model_dir, metadata)
            print("Local model is already downloaded and verified.", flush=True)
            return file
    url = f"https://huggingface.co/api/models/{MODEL_REPOSITORY}/revision/{MODEL_REVISION}?blobs=true"
    with urllib.request.urlopen(url, timeout=30) as response:
        metadata = json.load(response)
    license_name = metadata.get("cardData", {}).get("license")
    if license_name != "apache-2.0":
        raise RuntimeError(f"Expected Apache-2.0 model licensing; received {license_name!r}. Review the model card before downloading.")
    candidates = [entry for entry in metadata.get("siblings", []) if entry["rfilename"].lower().endswith("q4_k_m.gguf")]
    if len(candidates) != 1 or not candidates[0].get("lfs", {}).get("sha256"):
        raise RuntimeError("Could not locate one Q4_K_M model with an authoritative LFS SHA-256. No unverified model will be used.")
    model = candidates[0]
    revision = metadata["sha"]
    if revision != MODEL_REVISION or BASE_REPOSITORY not in metadata.get("cardData", {}).get("base_model", []):
        raise RuntimeError("The model revision or upstream model does not match the reviewed configuration.")
    filename = Path(model["rfilename"]).name
    expected = model["lfs"]["sha256"]
    url = f"https://huggingface.co/{MODEL_REPOSITORY}/resolve/{revision}/{urllib.parse.quote(model['rfilename'])}?download=true"
    target = model_dir / filename
    download(url, target, expected)
    projectors = [entry for entry in metadata.get("siblings", []) if entry['rfilename'].lower().startswith('mmproj-') and entry['rfilename'].lower().endswith('-f16.gguf')]
    if len(projectors) != 1 or not projectors[0].get('lfs', {}).get('sha256'):
        raise RuntimeError('Could not locate a checksum-verifiable vision projector.')
    projector = projectors[0]
    projector_name = Path(projector['rfilename']).name
    projector_hash = projector['lfs']['sha256']
    download(f"https://huggingface.co/{MODEL_REPOSITORY}/resolve/{revision}/{urllib.parse.quote(projector['rfilename'])}?download=true", model_dir / projector_name, projector_hash)
    with urllib.request.urlopen(f"https://huggingface.co/{MODEL_REPOSITORY}/raw/{revision}/README.md", timeout=30) as response:
        (model_dir / "MODEL-CARD.md").write_bytes(response.read())
    # Unsloth supplies the quantization; retain the license and model card
    # from the pinned official Qwen upstream as well as the quantizer's card.
    with urllib.request.urlopen(f"https://huggingface.co/api/models/{BASE_REPOSITORY}/revision/{BASE_REVISION}", timeout=30) as response:
        base_metadata = json.load(response)
    if base_metadata.get("cardData", {}).get("license") != "apache-2.0" or base_metadata["sha"] != BASE_REVISION:
        raise RuntimeError("The official base model's revision/license could not be verified.")
    with urllib.request.urlopen(f"https://huggingface.co/{BASE_REPOSITORY}/raw/{BASE_REVISION}/README.md", timeout=30) as response:
        (model_dir / "BASE-MODEL-CARD.md").write_bytes(response.read())
    license_source = f"https://huggingface.co/{BASE_REPOSITORY}/raw/{BASE_REVISION}/LICENSE"
    with urllib.request.urlopen(license_source, timeout=30) as response:
        license_text = response.read()
    if b"Apache License" not in license_text or b"Version 2.0" not in license_text:
        raise RuntimeError("The official model's Apache-2.0 license text could not be verified.")
    (model_dir / "LICENSE-model").write_bytes(license_text)
    record.write_text(json.dumps({"repository": MODEL_REPOSITORY, "revision": revision, "base_repository": BASE_REPOSITORY, "base_revision": BASE_REVISION, "filename": filename, "sha256": expected, "license": license_name, "license_source": license_source, "license_sha256": hashlib.sha256(license_text).hexdigest(), "projector": projector_name, "projector_sha256": projector_hash, "chat_template_kwargs": {"enable_thinking": False}, "reasoning": "off"}, indent=2))
    activate_model(model_dir, json.loads(record.read_text()))
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-only", action="store_true")
    parser.add_argument("--model", choices=MODEL_PROFILES, default=DEFAULT_MODEL, help="Verified model profile to install/select; defaults remain experimental")
    args = parser.parse_args()
    try:
        binary = setup_runtime()
        print(f"Runtime: {binary}", flush=True)
        if not args.runtime_only:
            model = setup_model(args.model)
            print(f"Model: {model}\nStart it with: python3 scripts/start_local_tutor.py", flush=True)
    except (urllib.error.URLError, OSError, RuntimeError, ValueError) as error:
        print(f"Local tutor setup incomplete: {error}", flush=True)
        print("If network access is denied, apply the saved GitHub/Hugging Face domain additions in environment settings, then rerun this command. No API key is required.", flush=True)
        raise SystemExit(1)
