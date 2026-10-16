"""Turn real-model responses into a readable review sheet; never grade answer quality."""
import argparse
import json
import math
import statistics
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit('Choose a new review filename to preserve previous reviewer notes.')
    report = json.loads(args.report.read_text())
    results = report['results']
    times = sorted(item['seconds'] for item in results if item['status'] == 200)
    failures = sum(item['status'] != 200 for item in results)
    lines = ['# StudyBuddy tutor review', '',
             'Reviewer: ______ · Date: ______ · Decision: unreviewed', '',
             'This sheet summarizes transport and timing only. Check answers, every diagram label, and the actual source pages against the reference criteria before scoring. A successful request is not a correctness pass.', '',
             f"Platform: {report['platform']}", '', f"Suite hash: `{report['suite_sha256']}`", '',
             f'Recorded requests: {len(results)}. HTTP failures: {failures}.', '']
    if times:
        p90 = times[math.ceil(len(times) * .9) - 1]
        lines.extend([f'Completed-request timings: median {statistics.median(times):.2f} s; p90 {p90:.2f} s (nearest rank); range {times[0]:.2f}–{times[-1]:.2f} s.', '',
                      'Failures remain in the review below. These timings apply only to the recorded machine and settings.', ''])
    if report.get('stopped_reason'):
        lines.extend([f"Incomplete run: {report['stopped_reason']}", ''])
    for item in results:
        lines.extend([f"## {item['id']} · trial {item['trial']} · PDF page {item['page']}", '',
                      f"HTTP {item['status']} · {item['seconds']} seconds", '',
                      '**Student request**', '', item['prompt'], '', '**Expected facts / review criteria**', '', item['reference'], '', '**Recorded response**', ''])
        if item['status'] != 200:
            lines.extend([str(item['response'].get('detail', item['response'])), ''])
        else:
            message = item['response']['messages'][-1]
            lines.extend([message['content'], '', 'Cited PDF pages: ' + ', '.join(map(str, message['citations'])), ''])
            visual = message.get('visual')
            if visual:
                lines.extend(['Diagram: ' + visual['title'], ''])
                nodes = {node['id']: node['label'] for node in visual['nodes']}
                lines.extend('- Node: ' + node['label'] for node in visual['nodes'])
                lines.append('')
                lines.extend(f"- {nodes.get(edge['source'], edge['source'])} → {nodes.get(edge['target'], edge['target'])}: {edge['label']}" for edge in visual['edges'])
                lines.append('')
        lines.extend(['**Review:** unreviewed · **Severity if failed:** ______ · **Reason and source check:** ______', ''])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text('\n'.join(lines))
    print(f'Review sheet written to {args.output}. No quality grade was assigned.')


if __name__ == '__main__':
    main()
