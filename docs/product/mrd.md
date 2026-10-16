# Marketing requirements document

Version 0.2 · October 16, 2026 · Market-facing brief for a product in development

Related: [vision](vision.md) · [requirements](prd.md) · [competitive evidence](competitive-analysis.md)

## Market opportunity

Students already combine lecture material, search, videos, peers, and AI assistants to study. The founder's experience suggests an opportunity within that existing behavior: help students resolve confusion while staying with the material their course actually uses, then check whether they can apply the idea.

This is an **opportunity hypothesis**, not a validated unmet market. Document chat, notes, source citations, and local models already exist in alternatives. StudyBuddy must show that its course-attached workflow and quality of feedback make a meaningful difference in a real study session.

The initial market is deliberately narrow: English-speaking college students in technical, slide-heavy courses who already use lecture PDFs and AI help. Initial recruitment is through the founder's reachable classmates. The first device target is an M3 Pro Mac with 18 GB memory; that hardware requirement limits the initial audience and must be considered when interpreting demand.

## Customer, user, and buying roles

| Segment | Job to accomplish | Priority and evidence |
| --- | --- | --- |
| Student preparing for a technical midterm | Understand an unfamiliar concept from course slides and solve a related problem | Primary; one founder-reported experience, independent interviews pending |
| Student reviewing lectures regularly | Resume prior explanations and practice without rebuilding context | Secondary hypothesis; repeat-use evidence pending |
| Tutor, teaching assistant, or instructor | Help students with course-aligned explanations and exercises | Possible later stakeholder/reviewer; no institutional buying need established |

The student is the initial user and possible future buyer. No school procurement strategy, institutional willingness to pay, or parent purchasing role has been validated. The pilot is free; future pricing and the business model are undecided. Using free/open-source resources does not itself decide whether the eventual product charges customers.

## Customer needs translated into market requirements

| Need | Evidence today | Product response | Validation question |
| --- | --- | --- | --- |
| N1 — Stay with the lecture while seeking help | Founder reports hours of searching across slides, videos, web, and AI | Menu-bar activation, floating tutor, and current-slide context from the active study window across apps; FR-01/02/12/13/14 | Does it reduce time and manual steps to a useful explanation compared with the student's usual workflow? |
| N2 — Keep useful study work where it belongs | Hypothesis; no independent observation yet | Saved per-slide notes, explanations, visuals, and export; FR-03/08/09 | Do students return to saved work in a later session without assistance? |
| N3 — Get understandable, correct, course-relevant help | Founder reports unresolved confusion; current model tests show reliability failures | Grounded answers, inspectable sources, visuals, honest uncertainty; FR-04/05/06 | Can the student apply the concept, and do references support the answer? |
| N4 — Check understanding through practice | Founder's requested product capability; benefit unvalidated | One question at a time and correct feedback; FR-07 | Does feedback identify the actual mistake and accept valid alternative reasoning? |
| N5 — Avoid paid AI dependencies and keep material local | Explicit founder constraint; broader student demand unvalidated | Free/open-source local stack and Mac setup; FR-10/11 | Can a participant install and use it on available hardware, and do they value that tradeoff? |

## Positioning and message requirements

Proposed positioning: **For students working through difficult lecture slides, StudyBuddy is a Mac menu-bar companion that follows their active study window across apps and keeps the right explanations, visual help, notes, and practice alongside it.**

Proposed short message: **“Understand the slide. Keep the explanation. Check what you learned.”** This is a message to test, not evidence of an achieved learning outcome.

Demonstrations should show a concrete session: open the menu-bar companion alongside the usual lecture app, advance a slide, ask a question, inspect its source, attempt a new problem, return to saved work. Present the deterministic Hamming lab as a guided example, and identify AI-generated content separately.

Market-facing claims must match the validated build. Claims about better grades, superiority to ChatGPT, knowledge of unrecorded professor explanations, exam prediction, or proven personalization are not supported. Describe the current product as an alpha until its [release gates](prd.md#6-release-gates) pass. Local inference is an available implementation choice; it is not exclusive to StudyBuddy.

## Competitive context

The main incumbent is the student's current workflow, especially ChatGPT plus lecture PDFs and assignments. Adjacent alternatives include NotebookLM, dedicated study tools such as StudyFetch/Knowt/Quizlet/RemNote, and open-source document assistants such as Open Notebook and AnythingLLM.

The [competitive analysis](competitive-analysis.md) separates verified repository evidence from background product descriptions that still need current verification. Source-grounded chat and local deployment are already available in verified open-source alternatives. StudyBuddy's proposed advantage must therefore be demonstrated through course-specific usability, dependable feedback, and repeat use.

## Market sizing and metrics

No defensible TAM, SAM, revenue forecast, or market-share estimate has been established. The founder's **5–10 reachable classmates** are a recruitment pool, not a market-size estimate. This report does not convert GitHub stars, website traffic, downloads, or general AI users into student customers.

To build a bottom-up estimate later, define a geography and term, identify students in the targeted course types, measure the fraction with recurring difficulty and suitable hardware, then measure trial and retention. A revenue estimate additionally needs an actual price test. Until those inputs exist, keep the model symbolic:

`eligible students × observed problem incidence × hardware/access fit × observed activation × observed retention`

These factors are currently unknown and should not be populated with optimistic guesses for a pitch.

## Entry strategy and validation

Start with a free founder session, then three observed classmate sessions after the PRD quality gates pass. Expand to five participants for a directional repeat-use check. The founder handles recruitment; no messages or posts are authorized or sent by this document. If available classmates take another course, use their own material and record that difference rather than claiming CYSE-specific validation.

Compare two different sections of similar difficulty using the student's normal tools and StudyBuddy; alternate which tool goes first. Record prior knowledge, elapsed time, copying/upload steps, clarification turns, incorrect claims, an unassisted application answer, and why the student chooses a tool for the next session. Do not teach the same question twice and count familiarity as an improvement.

Use a local session log or spreadsheet with participant codes. Collect only what the participant agrees to share; cloud analytics and paid research services are unnecessary for this pilot.

Proposed decision signals, not achieved results:

- At least three independent students describe or demonstrate the same recurring obstacle before a demo.
- At least four of five pilot students complete a useful session without the founder operating the product for them. Report missing participants instead of silently shrinking the denominator.
- At least three of five choose StudyBuddy again within seven days for an actual study task without a reminder being counted as voluntary return. Report reminder-assisted use separately.
- Critical tutoring errors block pilot expansion even if students like the interface.

A useful session means the student obtains help they can check, attempts a relevant application question, and saves or resumes their work. Small convenience-sample results guide the next iteration; they do not establish population-level learning improvement or product-market fit. If students consistently prefer their existing tools, revise the proposed advantage before adding integrations.

## Open research questions

How often does this problem occur outside the founder's experience? Is the main obstacle course notation, missing prerequisites, unreliable explanations, or workflow friction? Is slide-attached persistence valuable in later sessions? Can the free local approach run well on classmates' computers? What would students give up to use it? Would anyone make a real payment commitment after repeat use?

Resolve these through observed behavior and dated evidence. A positive response to “would you use this?” is not sufficient.
