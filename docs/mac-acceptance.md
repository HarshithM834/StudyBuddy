# Founder Mac acceptance session

Purpose: finish PRD G3 and provide the human review needed for G2/G4. Target: M3 Pro, 18 GB. This checklist is prepared, not executed on that Mac. Use the build linked with the handoff; preserve `.studybuddy/` when updating. Use [Mac companion setup](mac-companion.md) first.

## Record the setup

- Build/archive name and test date:
- macOS version, chip, and memory:
- First installation completed, or exact failing step:
- Model load time from `.studybuddy/logs/last-session.json`:
- Peak StudyBuddy/llama-server memory shown in Activity Monitor:

The diagnostic command prints environment/model/health information without course notes or credentials:

```bash
.venv/bin/python scripts/diagnose.py
```

## Verify the integration first (FR-12/13/14)

1. Build and launch the native app. Confirm a menu-bar book icon, no Dock app icon, and no required browser tab. Verify click-to-show/hide, drag/resize, and right-click Quit.
2. Before turning on study mode, check that no capture starts. Deny Screen Recording once and verify a useful explanation; then grant it through macOS settings and retry. Reopen if the OS requires it.
3. Open the course in Canvas. Turn on study mode. Confirm the panel labels the active app and shows the right window thumbnail. Switch to YouTube, PowerPoint or Preview and back: context should follow without choosing an app. Typing in the companion must not make it capture itself.
4. Attach the supplied Week 6 PDF. Test ten distinct readable slides and backtracking. Record every false match and uncertain match separately. Check a two-slide view, unrelated web content, zoom changes, and a page without readable text. A wrong confident page match fails this gate.
5. Ask a question on one slide, move to another before the response finishes, then return. The delayed answer and saved notes/diagram must belong to the original slide. Confirm unsent questions survive switching away and back in the current session.
6. Enable Explain as I go. Check one request per stable new recognized slide and no backlog while quickly paging. Existing explanations should restore. Pause during a pending capture and verify no late frame triggers a new request.
7. Hide the panel and reopen: capture stays paused. Right-click Quit and check Activity Monitor for owned service shutdown. Reopen and confirm saved course work restores. Check full-screen Canvas/video and multiple Spaces; report capture/visibility failures.
8. Test a visible YouTube frame and ask what the speaker said. It must disclose that no audio/transcript was received. Record errors; do not equate visible-frame capture with video understanding.

This checklist is unexecuted. After it passes, complete the study-quality and persistence journey below. Direct external-app drawing and audio ingestion are outside this alpha.

## Complete one study session

1. Start with `.venv/bin/python scripts/run.py`. Confirm the browser opens and a lecture can be uploaded. Import the original Week 6 PDF; confirm 44 pages. Reimport it and check that only one library item appears.
2. On PDF page 22, ask for X, Y and Z for data 1101. Check the actual explanation and cited page against the source. Correct result: XYZ=100. Use page numbers shown in StudyBuddy, not printed slide numbers.
3. Ask for a diagram of received 1111|100 with a single C error. Correct checks: X passes, Y and Z fail; corrected word 1101|100. Check every diagram label and citation.
4. On page 21, request one practice question and answer it. Confirm no answer is revealed before your attempt. Check that valid counting reasoning is accepted, not incorrectly rejected for using addition.
5. Save an explanation to notes, add your own text, highlight part of the page, and add a pin with text. Move away and return; confirm the same work restores and the other page has its own work.
6. Export the slide's notes. Open the Markdown file and check the lecture/page label, note text, pin text, and absence of another slide's work. Open the original PDF and verify it remains unchanged.
7. Reload the browser, then stop StudyBuddy with Control-C and restart it. Confirm the lecture, last location, notes, marks, conversation, and diagram restore.
8. Turn off Wi-Fi and disconnect any Ethernet, VPN, or other external connection. Start a new session with already-downloaded files. Ask a new question, save a note, and export it. Confirm a real answer arrives without external connectivity. Restore networking when finished.
9. Stop the session; run `.venv/bin/python scripts/run.py --workspace-only` with no separately running model. The PDF and notes must remain usable. Attempting to ask should show the offline state. If a request fails while the model is connected, the question must remain available for retry and notes must stay intact.
10. Navigate core controls by keyboard at your ordinary browser zoom. Open connection help, use Tab/Shift-Tab, and close it with Escape. Record any clipped or inaccessible controls.

Record the first failed step and what you expected versus observed. Screenshots should exclude unrelated personal material. A functioning connection alone does not establish correct tutoring.

## Quality and timing reports

Run the commands in the [evaluation guide](../evaluations/README.md): the 20-case screen plus repeated critical cases, and the fixed ten-prompt/three-repeat Mac timing sample. Review answers and actual source pages; record reviewer, date, pass/fail and reason per case. Keep failed requests in the report.

Release only when PRD G1–G4 pass. If a case still teaches something false, gives invalid feedback, contradicts its own diagram, or invents source/exam support, keep the build labeled alpha while it is fixed. Three-person classmate testing follows the founder gates.
