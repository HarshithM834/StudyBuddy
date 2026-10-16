"""Run the frozen tutor screen against the real local model without changing saved work."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import platform
import sys
import tempfile
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def fixture_pdf(pages: list[str]) -> bytes:
    from PIL import Image, ImageDraw, ImageFont
    images = []
    for text in pages:
        page = Image.new('RGB', (1200, 900), 'white')
        draw = ImageDraw.Draw(page)
        draw.multiline_text((50, 60), text, fill='black', font=ImageFont.load_default(size=27), spacing=18)
        images.append(page)
    output = io.BytesIO()
    images[0].save(output, 'PDF', save_all=True, append_images=images[1:])
    for image in images:
        image.close()
    return output.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdf', type=Path, help='The original CYSE 425 Week 6.pdf; not bundled in the source')
    parser.add_argument('--output', type=Path, default=ROOT / '.studybuddy/evaluations/week6-local.json')
    parser.add_argument('--suite', type=Path, default=ROOT / 'evaluations/week6-v1.json', help='Frozen reference suite; v1 is the regression set, v2 adds fresh cases')
    parser.add_argument('--cases', help='Comma-separated case IDs; default all 20')
    parser.add_argument('--critical-repeats', type=int, default=1, choices=range(1, 4), help='Total trials for D1/Q2/U1; use 3 for release screening')
    parser.add_argument('--repeat', type=int, default=1, choices=range(1, 4), help='Repeat every selected case, e.g. 3 for the Mac timing sample')
    args = parser.parse_args()
    suite_bytes = args.suite.read_bytes()
    suite = json.loads(suite_bytes)
    pdf = args.pdf.read_bytes()
    if hashlib.sha256(pdf).hexdigest() != suite['deck_sha256']:
        raise SystemExit('Supply the original CYSE 425 Week 6 PDF: this screen uses its exact page numbers.')
    cases = suite['cases']
    if args.cases:
        selected = args.cases.split(',')
        if set(selected) - {case['id'] for case in cases}:
            raise SystemExit('Unknown case ID. See evaluations/week6-v1.json.')
        cases = [case for case in cases if case['id'] in selected]
    trials = [(case, trial) for trial in range(1, max(args.repeat, args.critical_repeats) + 1) for case in cases
              if trial <= args.repeat or (case.get('critical_repeat') and trial <= args.critical_repeats)]
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise SystemExit(f'Report already exists: {output}. Choose a new --output to preserve previous evidence.')
    report = {'started_at_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'platform': platform.platform(),
              'suite_sha256': hashlib.sha256(suite_bytes).hexdigest(), 'review_required': True,
              'application_sha256': hashlib.sha256((ROOT / 'server/app.py').read_bytes()).hexdigest(),
              'suite_file': args.suite.name,
              'quality_pass': None, 'results': []}
    with tempfile.TemporaryDirectory(prefix='studybuddy-evaluation-') as temporary:
        os.environ['STUDYBUDDY_DATA_DIR'] = temporary
        # Only import after selecting isolated storage; never touch user notes.
        from fastapi.testclient import TestClient
        from server import app as application
        import httpx
        document = application.import_pdf(pdf, args.pdf.name, 'CYSE 425', 'cyse425-week6')
        with TestClient(application.app) as client:
            if not client.get('/api/health').json().get('tutor_configured'):
                raise SystemExit('Start the free local tutor first.')
            with httpx.Client(trust_env=False, timeout=5) as model_client:
                models = model_client.get(application.local_url() + '/v1/models')
                report['models'] = models.json() if models.is_success else {'status': models.status_code}
            report['vision_enabled'] = os.environ.get('STUDYBUDDY_LOCAL_VISION', '1') == '1'
            report['request_settings'] = {**application.TUTOR_SAMPLING, 'max_tokens': application.TUTOR_MAX_TOKENS, 'timeout_seconds': os.environ.get('STUDYBUDDY_TUTOR_TIMEOUT', '240')}
            output.write_text(json.dumps(report, indent=2))
            for number, (case, trial) in enumerate(trials, 1):
                current = document
                if case.get('fixture'):
                    current = application.import_pdf(fixture_pdf(case['fixture']), f"Synthetic {case['id']}.pdf", 'Synthetic evaluation fixture')
                page = case['page']
                # Each trial starts clean, except the first Q2 follows the actual Q1
                # if both were selected. Standalone/repeated Q2 gets fixed quiz context.
                continuing_quiz = case['id'] == 'Q2' and trial <= args.repeat and any(c['id'] == 'Q1' for c in cases)
                with application.database() as db:
                    if not continuing_quiz:
                        db.execute('DELETE FROM messages WHERE document_id=?', (current['id'],))
                    existing = db.execute('SELECT count(*) FROM messages WHERE document_id=? AND page=?', (current['id'], page)).fetchone()[0]
                    if not existing:
                        for message in case.get('prior', []):
                            db.execute('INSERT INTO messages(id,document_id,page,role,content) VALUES(?,?,?,?,?)', (uuid.uuid4().hex, current['id'], page, message['role'], message['content']))
                print(f"{number}/{len(trials)}: {case['id']} trial {trial}, page {page}, {case['intent']}…", flush=True)
                started = time.monotonic()
                response = client.post(f'/api/documents/{current["id"]}/pages/{page}/chat', json={'message': case['prompt'], 'intent': case['intent']})
                result = {'id': case['id'], 'trial': trial, 'page': page, 'intent': case['intent'], 'prompt': case['prompt'],
                          'seconds': round(time.monotonic() - started, 2), 'status': response.status_code, 'response': response.json(),
                          'reference': case['reference'], 'review': None}
                report['results'].append(result)
                output.write_text(json.dumps(report, indent=2))
                print(f"  HTTP {response.status_code}, {result['seconds']} s. Saved to {output}", flush=True)
    report['completed_at_utc'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    output.write_text(json.dumps(report, indent=2))
    print('Screen completed. HTTP success is not an accuracy pass: human review is required by PRD G2.')


if __name__ == '__main__':
    main()
