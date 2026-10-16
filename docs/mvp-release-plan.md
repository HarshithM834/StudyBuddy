# MVP execution checklist: October 15–18, 2026

This is the short execution view of the [product roadmap](product/roadmap.md). The [PRD](product/prd.md) is authoritative for requirements and acceptance; the [validation record](validation.md) reports actual results. Dates use America/New_York. October 18 is the usable **founder MVP target**, subject to PRD gates G1–G4.

## Fixed scope

Activate a native Mac menu-bar companion, turn on study mode to follow the active window across apps without choosing an app, and keep a floating tutor synchronized with the visible slide. Restore saved slide work on backtracking; offer optional explanations as the student moves. PDF import, source inspection, notes, and quiz support this workflow. Use free/open-source components and local inference on the founder's M3 Pro/18 GB. Lecture recording, drawings directly over external slide content, Drive/Outlook connections, accounts, billing, and public hosting are deferred.

## Checkpoints

| Date | Work | Evidence / current state |
| --- | --- | --- |
| Thu Oct 15 | Establish the product baseline; inspect real tutor behavior | Workspace checks passed; local model runs; answer-quality failures recorded; five product documents prepared |
| Fri Oct 16 | Build the menu-bar companion and window following; retain correctness and real Mac checks | Menu-bar shell and active-window companion source prepared; shared build, eighteen tests and simulated native UI flow passed. Tutor quality, native Mac build/capture and real performance checks remain open |
| Sat Oct 17 | Complete the founder journey and fix failures | Upload → navigate → ask → inspect source → answer → save → return/restart. Classmate trials may begin only after G1–G5 permit entry. Pending |
| Sun Oct 18 | Make the founder MVP release decision | Require G1–G4 and a matching source/setup handoff; otherwise retain alpha status and record remaining gates and a revised decision. Pending |

The October 16 clarification makes FR-12/13/14 release requirements. Broader model benchmarking and workspace polish yield priority to the native integration; tutor correctness is still required.

## Current open gates

- **G1/G3:** native build, permission behavior, window following, and per-slide restoration need actual Mac evidence.
- **G2:** tutoring correctness and completeness; the expanded 4B screen and bounded reasoning diagnostic both found critical errors. A larger local model is being evaluated.
- **G3:** actual Mac setup, full study journey, offline use, restart, and measured performance.
- **G4:** complete the handoff using the build validated on the Mac.
- **G5:** recruit three participants and enter the limited pilot after the founder MVP gates pass.

Cloud software checks provide evidence for G1; they do not close the model or Mac gates. See the PRD for the proposed evaluation thresholds and their rationale. No participant has been contacted on the founder's behalf, and none of these checkpoints represents a scheduled background task.
