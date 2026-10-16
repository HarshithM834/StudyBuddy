# Local tutor release screen

Maps to PRD FR-04 through FR-07 and G2. `week6-v1.json` freezes 20 prompts and reference criteria before the candidate model's first run: 5 explanations, 4 diagrams, 4 quiz/feedback cases, 4 uncertainty cases, and 3 source-quality cases. Six are the known development failures/checks; fourteen were new when frozen. Once inspected, later reruns are regression tests, not fresh held-out evidence. The reference criteria are never passed to the model.

The first 17 use the founder's original Week 6 PDF (not distributed). The last three generate isolated synthetic PDF scans for missing content, conflicting statements, and embedded instructions. They test source handling, not real-world OCR accuracy. PDF page numbers, not printed slide numbers, are used throughout.

With the model running:

```bash
.venv/bin/python scripts/evaluate_tutor.py '/path/to/CYSE 425 Week 6.pdf' \
  --critical-repeats 3 --output .studybuddy/evaluations/release-screen-1.json
```

This makes 26 requests: 20 cases plus two additional trials of each of the three critical regressions. Reports include source-suite hash, actual model metadata, platform, response/error, timings, and reference criteria. An existing report is never overwritten. Temporary storage protects the study workspace. Q2 follows Q1's actual quiz when both run; an isolated/repeated Q2 receives the same explicit quiz values as fixed context.

A separate reviewer must check each response, source page, and diagram against the reference. Record pass, noncritical fail, or critical fail with the reason and reviewer identity. PRD G2 requires at least 18/20 passes and zero critical errors across all trials. An HTTP 200, a matching keyword, or the generating model's own judgment is not a quality pass. The script deliberately leaves `quality_pass` and `review` unset.

A second frozen set, `week6-v2.json`, retains the six seeds and introduces fourteen fresh prompts/fixtures after the v1 failures. It was prepared before inspecting any 9B output. Use `--suite evaluations/week6-v2.json` for that screen; keep v1 as the regression set. Do not describe later reruns of either set as unseen data.

For a short development comparison, use `--cases E1,D1,Q1,Q2,U1,E2`. Do not treat six successful cases as the full release gate.

For the Mac timing sample, first warm up the model with one ordinary question, then run the fixed ten prompts three times:

```bash
.venv/bin/python scripts/evaluate_tutor.py '/path/to/CYSE 425 Week 6.pdf' \
  --cases E1,E2,E3,E4,E5,D1,D3,Q1,Q2,U1 --repeat 3 \
  --output .studybuddy/evaluations/mac-timing-1.json
```

Record cold startup separately, chip/RAM/macOS, runtime/model settings, and peak memory in Activity Monitor. Report all failures alongside median and p90 of completed requests. The PRD's proposed targets are median ≤30 seconds and p90 ≤60 seconds. Cloud CPU timings do not establish Mac performance.

## Prepare a readable human review

Convert a saved JSON report into a Markdown sheet with the actual answers, diagram nodes/edges, source pages, reference criteria, timings and blank review fields:

```bash
.venv/bin/python scripts/review_evaluation.py .studybuddy/evaluations/release-screen-1.json \
  --output .studybuddy/evaluations/release-screen-1-review.md
```

The converter calculates only HTTP failure counts and response-time statistics. It does not grade correctness or infer a release pass. It preserves prior files and labels interrupted runs. A qualified reviewer still needs to inspect the original PDF sources.
