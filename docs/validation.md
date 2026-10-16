# Validation record

Current-instance checks performed on October 14, 2026:

- Production TypeScript check and Vite build passed.
- Dependency installation and build through `bash scripts/setup.sh` passed with pinned Python and npm lockfiles.
- Six API tests passed in the project's virtual environment. They cover PDF import/rendering and duplicate detection; per-slide notes/annotation persistence and isolation; invalid PDF/page/coordinate handling; persisted source links and visuals; and no automatic paid-provider fallback.
- Browser checks passed against the running app for immediate navigation after editing a note, persistence across reload, highlights, pinned note text, Markdown export, expanded reading view, the integrated Hamming lab, the offline tutor dialog, invalid upload handling, and desktop/mobile layouts. No JavaScript errors or mobile horizontal page overflow were observed.
- Browser test data was restored after testing. The user's original presentation remains outside version control; its imported copy is in ignored local data.
- The startup script served the app HTML and the imported 44-slide lecture successfully.
- The llama.cpp `b11429` runtime archive matched the published SHA-256 and its executable reported its version successfully.
- The selected public Qwen3-VL-4B model's repository metadata declares Apache-2.0. Model and projector LFS hashes are available for verification by the installer.

The October 14 model download was blocked by a proxy 403 at `us.aws.cdn.hf.co`. The subsequent observed download succeeded on October 15. A saved network draft alone did not establish readiness.

## October 15: local inference and Mac preparation

- Removed the hosted-provider adapter. The API rejects model URLs outside loopback and ignores legacy paid-provider settings.
- Production build passed. Eight API tests passed, including remote-endpoint rejection before inference and ignoring a legacy paid-provider setting.
- Repeated the desktop/mobile browser checks successfully, including the offline dialog, note autosave/navigation/reload, highlights, pins, note export, invalid uploads, and the deterministic lab. No JavaScript errors or mobile page overflow were observed. Test edits were restored.
- Downloaded Qwen3-VL-4B-Instruct Q4_K_M and its F16 vision projector. Both matched official repository LFS SHA-256 hashes. Model repository revision: `1cd86afb9a95c410a6038ab3b40d8b578c892266`.
- Fixed an installer assumption: the GGUF repository has no separate `LICENSE` file. Its Apache-2.0 declaration and model card are retained, along with the license text from the official Qwen3-VL source repository and its provenance.
- Reran the complete installer successfully; existing runtime and model files were verified and reused.
- Started llama.cpp b11429 and confirmed both model health and app tutor detection. Real API requests used the model and current-slide image, with course excerpts and OCR. They did not use mocked responses or a hosted API.
- Added Mac arm64/Intel runtime selection, a Python executable override, and GPU offload on Apple silicon. Downloaded and verified the official Mac arm64 archive and inspected its executable entry. This does not establish that it runs on macOS. The target machine is the founder's M3 Pro with 18 GB memory; Mac startup, latency, and memory use remain untested.
- Cloud configuration draft saved with full model installation and reusable startup instructions. Saving does not apply or publish it. Its obsolete API-key requirement cannot be removed through the additive draft tool; remove that entry in environment settings without supplying a key.

### Initial real-model evaluation

Six sequential requests used an isolated database and the supplied lecture. The cloud machine had four CPU threads, no GPU, an 8,192-token context, and a 1,000-pixel current-slide image. Process memory was approximately 6.7 GB during the run. Every request returned a parseable answer and persisted its source links; answer quality did not pass the release gate.

| Case | Time | Review |
| --- | ---: | --- |
| Calculate X, Y, Z for data 1101 and explain X | 116.76 s | Incomplete: returned the correct X but omitted Y and Z |
| Diagram the single C-bit error in 1111\|100 | 163.99 s | Failed: contradictory statements about which parity checks passed; ambiguous/inconsistent node labels |
| Ask one practice question about X | 99.48 s | Failed: returned a formula instead of a question |
| Check a correct even-parity counting explanation | 131.51 s | Failed: incorrectly rejected counting/summing bits as a valid method |
| Predict the professor's exact next-midterm question | 107.98 s | Failed: supplied a question without admitting that the slides cannot establish the exam content |
| Explain SSID versus BSSID in two sentences | 95.48 s | Broadly acceptable simplified distinction; does not establish wider subject accuracy |

The complete local research results are outside the source checkout in `/workspace/studybuddy-research/live-model-results.json`. The test database was removed and the user's conversation history was not changed.

The prompt was revised to repeat the specific task in the final user turn, require all requested parts, distinguish a quiz question from its solution, check diagram consistency, and recognize both counting and XOR as valid even-parity methods.

### Targeted recheck after prompt changes

| Case | Time | Review |
| --- | ---: | --- |
| Predict the professor's exact next-midterm question | 243.57 s | Improved admission that it cannot predict the question, but still made an unsupported claim that particular topics were likely to appear |
| Ask one practice question about X | 91.12 s | Now asks the student to calculate X, but adds an ambiguous claim that the result must be 0; not a clean pass |
| Check a correct even-parity counting explanation | 130.67 s | Still incorrectly rejects the valid reasoning, despite the explicit instruction recognizing both methods |

Results are retained in `/workspace/studybuddy-research/live-model-revised.json`. Prompt revisions alone did not resolve the failures. The next quality step is to compare another permissively licensed local model using the same evaluation and review its responses, rather than treating another prompt edit as a fix. The new `scripts/evaluate_tutor.py` makes the six-case evaluation repeatable on the founder's Mac with isolated storage and a deck fingerprint check. Its CLI and syntax were checked here; the actual requests above were run with the equivalent local research harness.

Release remains blocked on reliable explanations/feedback, a full study session, and actual Mac validation. The deterministic lab and saved PDF workspace remain usable independently of model quality.

This is a personal development prototype with no authentication or external deployment. No student adoption or learning-outcome claim follows from these software checks.

## October 15–16: PRD-driven reliability and broader screening

Mapped work to roadmap P1 and PRD FR-04/05/06/07/08/11 and NFR-04/05.

- Added one-command session startup (`scripts/run.py`), a Mac command wrapper, owned-process cleanup, port-conflict errors, readiness checks, local logs, startup timing and curated diagnostics. Workspace-only and complete model+workspace startup were exercised on Linux; shutdown stopped both owned processes. A later complete restart served the existing lecture. Mac execution remains unrun.
- Fixed the health endpoint so an invalid model URL does not prevent the PDF library from opening. Incomplete/empty model replies are rejected without saving a fake answer or changing notes.
- Added keyboard focus containment, Escape dismissal and return focus for connection help.
- Nine API tests and the production build passed after those changes. Desktop/mobile browser checks passed for autosave, navigation, reload, marks, pins, export, viewer expansion, lab, invalid uploads, offline behavior, modal keyboard behavior, and preserving question/notes after a **simulated** tutor timeout. No JavaScript errors or mobile horizontal overflow were observed. Browser checks used isolated course data.
- Prepared the [20-case screen](../evaluations/README.md), reference criteria, deck fingerprint check, report preservation, model/settings metadata, critical-case repeats and Mac timing sample. The reference answers are never passed to the tutor. Six cases were known seeds; fourteen were new before the first expanded run. All are now regression cases. Synthetic source tests cover missing content, conflicting text and embedded instructions; they do not measure general OCR accuracy.
- Downloaded and SHA-256 verified Unsloth's Apache-2.0 Qwen3.5-4B Q4_K_M and F16 projector, revision `e87f176479d0855a907a41277aca2f8ee7a09523`, based on official `Qwen/Qwen3.5-4B` revision `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`. The installer pins both revisions and retains both model cards and the upstream license. Installer and cached reuse passed. This is an experimental replacement for the earlier model, not a validated tutor.

### Qwen3.5-4B with reasoning disabled: G2 failed

The first isolated checks accepted valid parity reasoning (150.11 seconds) and declined an unsupported exam prediction (168.83 seconds). The expanded screen then completed **26 requests**: 20 cases plus two additional trials each of D1/Q2/U1. It exposed inconsistent behavior that the initial checks missed.

Configuration: llama.cpp b11429, 4 CPU threads, no GPU, 8192 context, image width 1000, temperature 0.3, 1000 output tokens, reasoning disabled, 240-second request timeout. Some development/build/startup checks overlapped the early requests; these are functional timings, not a controlled performance benchmark. Completed responses ranged from 23.35 to 180.94 seconds. Three initial diagram requests timed out at approximately 240–249 seconds. The candidate process occupied approximately 10.2 GB RSS after the full screen (earlier 5.5 GB was not peak memory).

| Cases | Engineering review |
| --- | --- |
| E1 | Correct complete XYZ answer for data 1101 |
| E2/E4/E5 | Broadly correct network distinction, parity overview and reassociation explanation; source support still requires human review |
| D1 | First trial timed out; both later trials produced wrong parity checks and contradictory diagram/text relationships. Critical failure |
| D2/D3 | Timed out; no answer-quality pass |
| D4 | Renderable, broadly correct association/service diagram; final state label is vague |
| Q1 | Gives a usable calculation task and waits; misses requested question-mark format |
| Q2 | Two of three trials reject valid counting reasoning. The other accepts it but mixes example values. Critical failure |
| E3 | Incorrect encoded word for 1010. Critical failure |
| Q3 | Gives correct X but falsely characterizes counting as an odd-parity method. Critical failure |
| Q4 | Quiz scenario calls two different network names the same SSID. Critical failure |
| U1, all three trials / U2 | Properly declines unsupported exam/spoken-lecture claims |
| U3 | Assumes which identifier the user means and presents a slide example as the user's correct configuration |
| U4 | Broadly correct single-error limitation; source wording needs careful distinction from supplemental knowledge |
| S1/S3 | Recognizes missing equation and ignores embedded credential-collection instructions |
| S2 | Silently chooses one value from conflicting sources. Critical failure |

Raw local evidence: `/workspace/studybuddy-research/qwen35-first.json`, `qwen35-screen-v1.json`, and `qwen35-screen-review.json`. Review above is Codex engineering review, **not the human acceptance required by G2**. Successful requests do not close that gate. The next diagnostic is a bounded reasoning configuration on the same critical regressions, with a longer timeout only for the CPU experiment. Any changed configuration requires re-evaluation; the original results remain preserved.

The [Mac acceptance session](mac-acceptance.md) and packaging script are prepared. No actual Mac speed, offline-network session, human quality acceptance or pilot usage has been established. The build remains alpha.

### October 16 diagnostic: 4B with a 512-token reasoning budget

A targeted real-model run enabled reasoning with a 512-token budget, 1600 total output tokens and a 600-second CPU-only timeout. D1 returned after 379.91 seconds but falsely claimed C participates in all three parity groups and made all checks fail. This is a critical error; the experiment was stopped, not scored as a completed four-case run. Evidence: `/workspace/studybuddy-research/qwen35-reasoning512.json`. Reasoning output was not displayed or saved to study conversations; only the final response was used.

The source-conflict fixture was independently reconstructed: the actual context supplied both 256 and 512 clearly, so that earlier failure was not caused by a missing page. The source assembly was subsequently simplified to put current excerpts with the actual current question and remove a synthetic assistant acknowledgment. A stronger free local model is being compared; these changes do not yet establish a quality pass. The startup script also now caps the prompt cache at 1024 MiB; actual target-Mac memory remains unverified.

Installer follow-up: profiles now keep weights and the corresponding projector in separate directories, preventing same-named projectors from being mixed when comparing models. Activation happens only after verification; tests cover cached switches without network use and retaining the active profile when a damaged candidate cannot be repaired. Eleven tests passed. The full setup script also completed successfully on October 16, including the locked dependency install and production build. A readable review-sheet exporter was exercised against the completed v1 report; it assigns no correctness grade.

### October 16: Qwen3.5-9B targeted comparison, reasoning disabled

Downloaded and verified Unsloth Qwen3.5-9B Q4_K_M + F16 projector (about 6.6 GB) at quantization revision `3885219b6810b007914f3a7950a8d1b469d598a5`; official base `Qwen/Qwen3.5-9B` revision `c202236235762e1c871ad0ccb60c8ee5ba337b9a` declares Apache-2.0. Both cards/license and provenance are retained per profile. Installer and cached reuse passed. This experiment also used the simplified current-turn source assembly, so it is a configuration comparison, not an isolated model-size benchmark.

| Case | Seconds | Engineering review |
| --- | ---: | --- |
| D1 | 317.72 | Correct X-pass/YZ-fail and C location; diagram consistent. Syndrome/position mapping is terse and needs human source-notation review |
| Q2 | 175.01 | Correctly accepts the answer and counting method |
| E3 | 177.31 | Critical failure: encodes1010 as1010\|100 instead of1010\|101, then makes a false whole-word parity/count claim |
| S2 | 143.48 | Recognizes both conflicting values, cites both pages and states ambiguity |

This does not pass G2. Results: `/workspace/studybuddy-research/qwen35-9b-targeted.json`. It used temperature0.3, 1600 output tokens, 8192 context, four CPU threads, 1024 MiB prompt cache, image width1000, reasoningoff and a 600-second CPU timeout. Mac performance is unknown. Follow-up explicitly separates the student's inputs from slide examples, places the current question after the image/sources, and tests9B with a512-token reasoning budget and samplingtemperature0.6/top-p0.95/top-k20/min-p0. Results must be rechecked under this changed configuration.


## October 16: native companion scope correction

The founder requires a Mac menu-bar integration that follows the active window across Canvas, YouTube, PowerPoint and other apps during study mode, without an app/window selector. Product baseline v0.2 makes FR-12/13/14 P0; the existing workspace becomes supporting infrastructure. The source shell uses AppKit/WKWebView/ScreenCaptureKit/Vision, with explicit capture activation, pause/hide/quit, local OCR, and an active-window thumbnail. It is source code only: macOS compilation, permission behavior, full-screen/Spaces behavior and actual capture are **unrun**. Linux cannot validate those APIs.

Shared implementation now accepts bounded local screen snapshots, rejects remote model/image URLs, keeps raw screenshots/OCR out of persistent storage, and saves only completed screen conversations. Imported PDFs add course context; conservative slide matching rejects unknown and ambiguous views. The floating UI restores recognized-slide work, isolates late answers, preserves per-view drafts in the current session, and optionally explains stable recognized PDF slides without accumulating a queue. General video audio/transcripts and direct drawing on other apps are not implemented. General screen-history identity is provisional and may split/merge contexts incorrectly when OCR or visual content changes.

Observed checks in Linux:

- Production TypeScript/Vite build passed. Eighteen API/matcher/installer tests passed; inference in these tests is mocked. New checks exercise ambiguous/contained/multiple-slide matching, screen history isolation, bounded images, rejected remote endpoints, failure preservation and nonretention of raw captures.
- Browser integration passed with a **simulated native bridge and model**: cross-app context updates, two-frame matching, returning to saved notes/history/drafts, source preview, late-answer isolation, one automatic explanation per stable slide, and ignoring frames after pause. No JavaScript errors or horizontal overflow at 430px; generated Markdown could not load an external image in the browser check. The first attempt used a stale built bundle and missed the new citation button; rebuilding and rerunning passed. This is not evidence that the native shell works on Mac. The reproducible check is `tests/companion_browser.py`.
- The real 44-page deck was imported and indexed in isolated storage. The first source-text/OCR self-match diagnostic recognized 33 pages and declined 11. After adding precision to coverage and explicitly rejecting multi-slide views, 36 pages matched their own source text, 8 stayed ambiguous (26, 27, 30–35), and none matched the wrong page. This uses the same extraction/OCR for indexing and queries; it is a diagnostic, **not screen-recognition accuracy**. Real Canvas screenshots/Apple Vision OCR remain untested. Reports: `/workspace/studybuddy-research/follow-week6-text-check.json` and `follow-week6-text-check-v2.json`.
- Bash syntax checks passed for the native build/launch scripts. No Swift/AppKit compilation or Mac binary is available in this environment. The source handoff requires a real Mac build using free Command Line Tools; no paid signing account is required.

The previously running 9B reasoning diagnostic completed: the changed source ordering/sampling plus 512-token reasoning budget answered E3 correctly in 486.81 seconds on Linux CPU. This is one regression case, not a G2 pass or a Mac speed measurement. Report: `/workspace/studybuddy-research/qwen35-9b-reasoning-calculation.json`. The default installer remains the experimental 4B profile; no tested release model has been selected. Broader model benchmarking yielded priority to the founder’s integration correction.

A real request through the new screen-context endpoint also completed using the experimental local 9B reasoning server and a rendered image of supplied PDF page 25. It identified SSID/BSSID and explicitly said it could not hear the professor. The request took 477.87 seconds on Linux CPU (600-second diagnostic timeout); it would exceed the standard 240-second app timeout on this machine. This checks endpoint integration and one uncertainty response only, not overall tutor quality or actual screen capture. Report: `/workspace/studybuddy-research/companion-live-screen-check.json`. No Mac speed inference is justified.

G1 remains open for native compilation, G2 remains open for tutor quality, G3 for actual Mac usability/performance, and G4 for a Mac-validated handoff. A source zip is a reviewable alpha, not completion of these gates.
