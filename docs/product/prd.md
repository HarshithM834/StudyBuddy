# Product requirements document

Version 0.2 · October 16, 2026 · Status: working baseline; release gates open

Related: [vision](vision.md) · [MRD](mrd.md) · [roadmap](roadmap.md) · [validation](../validation.md)

## 1. Product and release objective

Deliver a Mac menu-bar companion that floats beside the student’s existing lecture app, follows the active study window across apps, offers help about the visible slide, and restores saved explanations when the student returns. Importing a PDF supplies course context; the existing workspace is a supporting material/notes view, not the primary product. The first target is the founder's M3 Pro Mac with 18 GB memory.

**October 18, 2026 is the target for a usable founder MVP.** A successful build or model connection does not meet that definition. The quality, usability, performance, and setup gates below must pass. If they do not, keep the build labeled alpha and revise the date or approach explicitly. Do not silently lower the correctness standard to meet the date.

## 2. Audience, problem, and evidence

The initial audience is students in slide-heavy technical college courses who already study from lecture PDFs, class assignments, and general AI tools. The first user is the founder; classmates are prospective pilot participants, including students from other courses. English-language technical PDFs are the initial evaluation scope. Broader subjects, languages, and machines require further validation.

The founder reports that simpler explanations from ChatGPT still did not resolve Hamming-code confusion. Classmates' use of ChatGPT is founder-reported; their actual obstacles and preferences have not been observed. The [MRD](mrd.md) maps those hypotheses to research questions.

The proposed advantage is less repeated context setup and a study session that remains attached to the lecture. Uploading documents, generating notes, and asking AI questions already have substitutes. We must demonstrate usefulness and repeat use rather than assume differentiation from a feature list.

## 3. Main user journey

1. Launch StudyBuddy once; click its Mac menu-bar icon to show a small movable floating companion.
2. Add the lecture PDF as course context, open that lecture in the student’s usual app, and turn on study mode.
3. Allow macOS Screen Recording access when following is requested. Follow the frontmost ordinary window as the student switches apps, excluding the companion itself, while study mode is active; show a persistent status and Pause control.
4. Recognize the visible slide and attach the existing per-slide conversation, notes, and visuals. If the PDF match is uncertain or two slides are equally visible, say so and use visible-screen context without claiming a PDF identity. Course attachment is optional; Canvas, YouTube, PowerPoint, and other active windows use the same capture path.
5. Ask for an explanation, visual, or quiz in the floating panel. An optional “Explain as I go” switch requests an explanation after a stable newly recognized slide, reuses saved explanations, and queues at most the latest slide while the tutor is busy.
6. Move forward, then back: restore the correct slide’s work. A response for an earlier slide must never appear as an answer for the current one.
7. Hide or pause the companion to stop capture; reopening it does not silently resume capture. Quit from the menu bar. Notes remain after restart.

The October 16 founder clarification makes the menu-bar integration and following the material **P0**, replacing the earlier workspace-first delivery sequence. The founder studies in Canvas and explicitly rejected per-app/window selection. Study mode follows the active window across apps automatically. Capture compatibility and semantic understanding must be tested separately: one screenshot cannot supply a video’s audio, hidden content, or an entire document. Imported PDFs provide additional course context and stable page identity. For other windows, saved history currently uses normalized visible text plus window/application identity (and the image for text-poor views); changes in OCR/zoom/video captions can prevent restoration. That limitation remains open. Text and diagrams appear in the companion beside the original app; drawing directly over external slide content remains later work.

## 4. Functional requirements

All FR requirements below are **P0: required for the usable MVP**, except the explicitly identified existing demo. “Implemented” describes code, not a passed release gate. Needs N1–N5 are defined in the [MRD](mrd.md).

| ID | Requirement and student need | Acceptance check | Current state |
| --- | --- | --- | --- |
| FR-01 | Import and read PDFs; N1 | Accept PDFs up to 32 MB and 250 pages; reject invalid/oversized files with an understandable error; render the supplied 44-page lecture; duplicate import does not create another copy | Implemented; cloud API/browser checks passed |
| FR-02 | Navigate the lecture; N1 | Thumbnails, next/previous, slide-title search, and saved last location work; page numbering is consistently identified as PDF page numbers | Implemented; cloud checks passed |
| FR-03 | Keep work with its slide; N2 | Notes, highlights, pins, conversations, and diagram data survive navigation, reload, and app restart; notes/annotations do not appear on other slides/documents; original PDF remains intact | Implemented; navigation/reload/isolation checked; complete Mac restart journey pending |
| FR-04 | Answer in course context; N3 | Use the current page and relevant provided excerpts/images; address all requested parts; preserve relevant notation; distinguish additional explanation from source claims; admit unreadable or missing evidence | Implemented; live answer-quality gate failed |
| FR-05 | Provide inspectable sources; N3 | Source links open the stated pages; supplied-page filtering works; a human review confirms the cited material actually supports each course-specific claim | Link/filter mechanics implemented; semantic support gate open |
| FR-06 | Explain visually when requested; N3 | A small labeled diagram renders, agrees with the answer and source, and restores with its slide; do not imply that a generic graph is a precise equation or circuit drawing | Implemented; live consistency check failed |
| FR-07 | Quiz and check reasoning; N4 | Ask one clear application question with sufficient information; wait before revealing its answer; evaluate the student's attempt correctly, including valid alternative methods; make no mastery claim from one answer | Implemented; real quiz/feedback checks failed |
| FR-08 | Preserve work when AI fails; N2/N3 | Clearly show unavailable model, request failure, or incomplete response; retain the question for retry and preserve notes; PDF/notes remain usable without a model | Error paths implemented; offline browser/API checks passed |
| FR-09 | Export slide notes; N2 | Markdown export contains the selected slide's notes and pinned text with the lecture/page identity, without another slide's content | Implemented; browser check passed |
| FR-10 | Run without paid services; N5 | Local model only; reject remote inference endpoints; legacy paid-provider settings cannot activate a paid adapter; after installation, demonstrate a complete session with external networking disabled | Local-only enforcement tested; complete offline Mac session pending |
| FR-11 | Start on the target Mac; N5 | A clean source-folder setup and a later restart work on the actual M3 Pro/18 GB; repeated setup reuses valid downloads; instructions describe prerequisites and failure recovery | Installer/scripts prepared; Apple archive verified; execution unverified |
| FR-12 | Menu-bar presence and floating help; N1 | Native Mac app has a menu-bar icon; click toggles a movable, resizable panel above the lecture; it is absent from the Dock; Quit stops only its owned services; no browser tab is required | Native shell code written; Mac build/run unverified |
| FR-13 | Follow the active window across apps; N1/N5 | Explicit study-mode activation and macOS permission; no app/window selector; visible active/paused/uncertain status; test Canvas → YouTube → PowerPoint/Preview transitions; recognize at least ten tested single-slide transitions on the founder’s PDF, including backtracking; decline ambiguous/unknown content; hiding/pausing/quitting stops capture; capture only the active ordinary window, not the desktop or the companion | Native capture code written; Linux API tests passed; Mac capture unverified |
| FR-14 | Keep help synchronized while reading; N1/N2 | Confirm a stable slide before switching; restore its notes/explanations/diagrams; preserve edits and questions; keep late answers attached to their original slide; optional automatic explanation has no duplicate queue and stops when following pauses | Companion UI and simulated-bridge browser checks passed; Mac journey pending |

The deterministic CYSE 425 Hamming lab is an **existing optional demo**, labeled as such. Its verified calculations are useful supporting functionality. It does not satisfy FR-04, FR-06, or FR-07 for general tutoring and is not a substitute for evaluating model answers.

## 5. Nonfunctional requirements and boundaries

| ID | Requirement | Proposed verification |
| --- | --- | --- |
| NFR-01 | Free, open-source resources | Record dependency/model license and provenance; require no paid API, trial credit, subscription, or paid hosting to complete the MVP journey; preserve notices. This does not promise zero hardware/electricity cost or a permanently free future business model |
| NFR-02 | Local data handling | Store course material and learning work locally; no analytics or silent cloud uploads; verify no external inference request in the offline session. Future account connections require explicit student control and a separate scope decision |
| NFR-03 | Useful response time on the target Mac | Proposed target: median ≤30 s and p90 ≤60 s for completed short responses across 10 fixed prompts run three times after model warm-up; record model, settings, failures, memory, and separate cold-start time. Do not discard failed requests from the report |
| NFR-04 | Readable and usable controls | Core workflow works with keyboard focus, readable labels, and a narrow native Mac panel; desktop is the release target. The supporting web view remains useful for development |
| NFR-05 | Visible failures and stable saved work | No silent loss of notes or fake successful AI responses; show busy/error state; preserve saved work across model failure and restart. No accounts or public multi-user service in this release |

The speed thresholds and evaluation sample below are **proposed working acceptance targets**, introduced to make “usable” testable. They are not measured Mac performance or separately approved founder commitments. The existing cloud responses took about 91–244 seconds and do not establish target-machine performance.

## 6. Release gates

| Gate | Evidence required | Current result |
| --- | --- | --- |
| G1 — Software | Production build and relevant API checks pass; browser persistence/error checks pass; repeat core checks after relevant changes | Cloud build and eighteen tests passed; companion browser simulation passed. Model transport is mocked and installer tests use inert artifacts. Native macOS build/run remains unverified, so G1 is still open |
| G2 — Tutor quality | Pass the human-reviewed evaluation below on the intended runtime/model; no unresolved critical teaching, feedback, or source error | Failed; expanded Qwen3.5-4B screen found critical calculation, feedback, diagram and source-conflict errors |
| G3 — Mac usability and speed | Founder completes FR-01 through FR-14 journey, including export, restart, offline use, and NFR-03 measurement on M3 Pro/18 GB | Not run |
| G4 — Reproducible handoff | Setup instructions and source bundle match the tested build; licenses/download verification retained; known limitations recorded | Source bundle and instructions exist; complete Mac handoff pending |
| G5 — Limited pilot entry | G1–G4 pass; at least three participants recruited for observed sessions, with their own suitable course material | Not run; no one contacted on founder's behalf |

**Release rules:** G1–G4 permit the founder MVP. G5 opens the limited classmate pilot. None permits a public multi-user launch, claims of learning effectiveness, or claims of product-market fit. A founder can test the alpha while these gates are open, with its limitations visible.

### Tutor evaluation protocol for G2

Use 20 cases: five explanations/calculations, four diagrams, four quiz/feedback turns, four unsupported/ambiguous questions, and three cases involving unreadable content, conflicting material, or instructions embedded in a document. Include all six existing Week 6 seed cases and 14 additional cases not used to tune the prompt. Include concepts beyond Hamming; evaluate another course deck before generalizing beyond the initial lecture.

Prepare expected facts/acceptable reasoning and supporting pages or authoritative worked references before scoring. Review answers against those references; do not let the generating model grade itself. Use a reference-capable reviewer for disputed technical claims rather than treating the confused student's approval as correctness.

Proposed pass standard: at least 18/20 are complete, correct, appropriately sourced, and appropriate to the requested interaction, with **zero critical errors**. Wrong teaching facts, rejection of valid reasoning, contradictory diagrams, fabricated source support, and invented exam/professor claims are critical. Noncritical issues include wording or incomplete presentation that makes no false claim. Repeat the three existing critical cases—diagram consistency, valid parity reasoning, and unsupported exam prediction—three times each after changes; any critical failure keeps G2 open. This small evaluation is a release screen, not a scientific accuracy or learning-outcome estimate.

The [evaluation guide](../../evaluations/README.md) now runs all 20 frozen cases and critical-case repeats. The first expanded run is recorded in [validation](../validation.md). Those cases are now regression cases; a second set with fourteen fresh cases is frozen as `evaluations/week6-v2.json` for the next configuration. Human review and actual Mac validation remain open.

## 7. Out of scope for this MVP

Lecture recording/transcription, voice/automatic narration, drawings anchored over external app content, always-on background recording while study mode is off, app control, Drive/Outlook connections, full-course mind maps, assignment ingestion beyond PDF, long-term adaptive mastery models, accounts, billing, synchronization, public hosting, and native Windows/mobile distribution are deferred. The [roadmap](roadmap.md) retains their intent without promising dates.

## 8. Risks, dependencies, and decision ownership

- **Native integration is now a release blocker alongside answer quality.** macOS APIs cannot be validated by Linux browser tests. A source build needs the free Apple Command Line Tools; there is no paid Developer Program or notarized distribution in this alpha.
- **Answer quality remains a blocker.** Compare another permissively licensed local model using the same cases if needed; do not treat a larger model or a prompt edit as a verified fix.
- **Mac performance is unknown.** Hardware access and an actual run are required. Model changes must preserve the free/local constraint and fit the target machine.
- **Course context is incomplete.** Slides do not reveal what was said in class or what will be on an exam. Additional sources belong in a later, explicit scope decision.
- **Value over existing tools is unproven.** Follow the MRD comparison and repeat-use experiment before expanding features.
- **Deadline pressure:** reduce scope or adjust the target openly if gates fail; never relabel wrong feedback as acceptable.

The founder owns priorities, target-machine testing, participant access, and the release decision. Codex owns implementation and reproducible technical evidence during active work. Reviewers need to resolve technical correctness with references. Research outreach, publication, and paid spending are not automatically authorized by this document.
