"""Start a local study session and stop only the processes this launcher owns."""
from __future__ import annotations

import argparse
import json
import os
import platform
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get("STUDYBUDDY_DATA_DIR", ROOT / ".studybuddy"))
# Loopback requests must not go through a corporate/system HTTP proxy.
LOCAL_HTTP = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def occupied(port: int) -> bool:
    with socket.socket() as connection:
        connection.settimeout(0.3)
        return connection.connect_ex(("127.0.0.1", port)) == 0


def healthy(port: int, path: str) -> bool:
    try:
        with LOCAL_HTTP.open(f"http://127.0.0.1:{port}{path}", timeout=2) as response:
            data = json.load(response)
            return response.status == 200 and data.get("status") == "ok"
    except (OSError, ValueError, urllib.error.URLError):
        return False


def wait_ready(process: subprocess.Popen, port: int, path: str, log: Path, seconds: int):
    deadline = time.monotonic() + seconds
    next_update = time.monotonic() + 15
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"Startup exited with code {process.returncode}. See {log}.")
        if healthy(port, path):
            return
        if time.monotonic() >= next_update:
            print(f"Still starting… details in {log}", flush=True)
            next_update += 15
        time.sleep(0.5)
    raise RuntimeError(f"Startup did not become ready within {seconds} seconds. See {log}.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-only", action="store_true", help="Use PDFs and notes without starting a tutor")
    parser.add_argument("--no-browser", action="store_true", help="Do not open the default Mac browser")
    args = parser.parse_args()
    python = ROOT / ".venv/bin/python"
    if not python.is_file() or not (ROOT / "dist/index.html").is_file():
        raise SystemExit("Install the workspace first: bash scripts/setup.sh")
    try:
        port = int(os.environ.get("STUDYBUDDY_PORT", "8000"))
        if not 1024 <= port <= 65535 or port == 8081:
            raise ValueError
    except ValueError:
        raise SystemExit("STUDYBUDDY_PORT must be 1024–65535, excluding tutor port 8081.")
    if occupied(port):
        raise SystemExit(f"Port {port} is in use. Stop the previous workspace or set STUDYBUDDY_PORT to another port.")
    # This launcher manages a known loopback server; no remote URL is inherited.
    environment = dict(os.environ, STUDYBUDDY_LOCAL_URL="http://127.0.0.1:8081")
    logs = DATA / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    processes: list[subprocess.Popen] = []
    handles = []

    def start(command: list[str], name: str):
        path = logs / f"{name}.log"
        handle = path.open("a", encoding="utf-8")
        handles.append(handle)
        handle.write(f"\n--- Session {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        handle.flush()
        process = subprocess.Popen(command, cwd=ROOT, env=environment, stdout=handle, stderr=subprocess.STDOUT, start_new_session=True)
        processes.append(process)
        return process, path

    def interrupt(_signum, _frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, interrupt)
    result = 0
    session = {"platform": platform.platform(), "started_at_utc": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
               "workspace_only": args.workspace_only, "model_reused": False, "model_start_seconds": None}
    try:
        if not args.workspace_only:
            if occupied(8081):
                if not healthy(8081, "/health"):
                    raise RuntimeError("Port 8081 is occupied by a server that is not ready. Check the existing tutor or stop it first.")
                print("Using the local tutor already running on port 8081; it will remain running when this session ends.", flush=True)
                session["model_reused"] = True
            else:
                print("Starting the free local tutor…", flush=True)
                started = time.monotonic()
                process, log = start([str(python), "scripts/start_local_tutor.py"], "tutor")
                wait_ready(process, 8081, "/health", log, 180)
                session["model_start_seconds"] = round(time.monotonic() - started, 2)
        print("Starting your study workspace…", flush=True)
        started = time.monotonic()
        process, log = start([str(python), "-m", "uvicorn", "server.app:app", "--host", "127.0.0.1", "--port", str(port)], "workspace")
        wait_ready(process, port, "/api/health", log, 30)
        session["workspace_start_seconds"] = round(time.monotonic() - started, 2)
        (logs / "last-session.json").write_text(json.dumps(session, indent=2))
        print(f"StudyBuddy is ready on this computer's port {port}. Press Control-C to end the session. Logs: {logs}", flush=True)
        if not args.no_browser and platform.system() == "Darwin":
            webbrowser.open(f"http://127.0.0.1:{port}")
        while True:
            for child in processes:
                if child.poll() is not None:
                    raise RuntimeError(f"A StudyBuddy process stopped (exit {child.returncode}). Your saved work remains in {DATA}. Check {logs}.")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping this session. Your saved work stays on this machine.", flush=True)
    except (OSError, RuntimeError) as error:
        print(f"StudyBuddy could not continue: {error}", file=sys.stderr)
        result = 1
    finally:
        for child in reversed(processes):
            if child.poll() is None:
                child.terminate()
                try:
                    child.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait()
        for handle in handles:
            handle.close()
    return result


if __name__ == "__main__":
    raise SystemExit(main())
