"""Print setup information without reading course material, credentials, or conversations."""
import json
import os
import platform
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get("STUDYBUDDY_DATA_DIR", ROOT / ".studybuddy"))


def command(args):
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL, timeout=5).strip()
    except (OSError, subprocess.SubprocessError):
        return None


def main():
    report = {"platform": platform.platform(), "architecture": platform.machine(), "python": platform.python_version(),
              "node": command(["node", "--version"]), "ocr_available": bool(shutil.which("tesseract")),
              "frontend_built": (ROOT / "dist/index.html").is_file()}
    if platform.system() == "Darwin":
        report.update({"macos": command(["sw_vers", "-productVersion"]), "chip": command(["sysctl", "-n", "machdep.cpu.brand_string"]),
                       "memory_bytes": command(["sysctl", "-n", "hw.memsize"])})
    record = DATA / "models/model.json"
    if record.exists():
        model = json.loads(record.read_text())
        report['model'] = {key: model.get(key) for key in ['repository', 'revision', 'filename', 'sha256', 'projector', 'license', 'chat_template_kwargs', 'reasoning']}
        report['model_files_present'] = all((DATA / 'models' / model.get(key, 'missing')).is_file() for key in ['filename', 'projector'])
    else:
        report['model_files_present'] = False
    # Health requests only. Do not inspect documents or dump environment values.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    for name, port, path in [('workspace', os.environ.get('STUDYBUDDY_PORT', '8000'), '/api/health'), ('tutor', '8081', '/health')]:
        try:
            if not port.isdigit() or not 1 <= int(port) <= 65535:
                raise ValueError('Invalid port')
            with opener.open(f'http://127.0.0.1:{port}{path}', timeout=4) as response:
                report[name] = json.load(response)
        except (OSError, ValueError) as error:
            report[name] = {'available': False, 'reason': type(error).__name__}
    session = DATA / 'logs/last-session.json'
    if session.is_file():
        report['last_session'] = json.loads(session.read_text())
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
