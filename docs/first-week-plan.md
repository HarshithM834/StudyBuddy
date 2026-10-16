# StudyBuddy: first experiment

This file retains the original **research protocol**, not the current release schedule. The [product baseline](product/README.md), [PRD](product/prd.md), and [roadmap](product/roadmap.md) now govern scope and dates. Conduct participant product trials only after the PRD pilot-entry gate passes; discovery interviews can happen earlier.

## Decision to make

Does tutoring beside a student's actual lecture slides solve a recurring problem well enough that the student chooses it again while ChatGPT remains available?

Start with one difficult lecture and a few students. The first milestone is a useful study session followed by voluntary reuse. This experiment does not establish product-market fit or educational effectiveness.

## What we know

- The founder struggled to understand CYSE 425 RF Communications lecture slides while preparing for a midterm.
- Searching Udemy, YouTube, Google, and AI did not resolve that struggle efficiently.
- Five to ten classmates are reachable, although they may be taking a different course.
- A friend raised the central alternative: upload the same material to ChatGPT and ask questions there.
- The founder supplied the 44-page CYSE 425 Week 6 deck and identified Hamming code as the unresolved difficulty. Asking ChatGPT for a simpler explanation, including a five-year-old explanation, did not resolve it.
- The founder reports that classmates use ChatGPT, lecture presentations, and in-class assignments. Their satisfaction and pain points have not yet been observed.
- A React/FastAPI workspace now imports PDFs, preserves slide notes/highlights/pins, and includes the Hamming visual lab. The tutor uses local llama.cpp inference only. See `docs/validation.md` for the latest measured results, `README.md` for startup, and `docs/open-source-stack.md` for dependencies and costs.
- The founder redirected the work from teaching them in chat to building the product. Product implementation and validation are the active task; further unsolicited lectures are not part of that task.
- The standalone Hamming walkthrough in `prototypes/hamming.html` remains an earlier interaction experiment with fixed explanations. See `docs/week6-pilot.md` for its source mapping.
- No demand, willingness to pay, or learning benefit has been validated.

## Research step 1: reconstruct the problem

Founder provides one troublesome lecture deck, identifies two or three confusing slides, and shares the questions they tried asking AI. A deck from another current course is suitable if it represents the same difficulty and makes recruiting easier.

Invite three classmates to a 20-minute session. Prefer students taking the same technical course where practical. Ask them to bring material from a recent difficult study session.

Suggested invitation:

> I'm exploring a study tool and want to understand where studying lecture slides gets difficult. Could you spend 20 minutes showing me a recent confusing slide and how you tried to understand it? Bring whatever tools you normally use, including ChatGPT.

During each session:

1. Ask what they were preparing for and what specifically they could not understand.
2. Have them show the slide and their actual search or AI conversation, if available.
3. Observe them tackling a fresh confusing part with their usual tools.
4. Record the obstacle: missing prerequisite, notation, linking sources to the slide, checking correctness, or something else.
5. Ask what they did next and whether they eventually solved the problem.

Record observations separately from opinions about the proposed product. Do not treat a "yes, I'd use it" response as demand. Research participants should use their own accounts; no credentials are needed by us.

Deliverable: three short session notes and a selected recurring obstacle. If the obstacle differs from our hypothesis, revise the prototype scope before building.

## Research step 2: evaluate one complete interaction

Subject to the observed obstacle, the proposed prototype is a browser-based PDF study workspace:

- Open a lecture deck and navigate its slides.
- Select a passage or ask about the current slide without manually copying it into another conversation.
- Receive an explanation grounded in relevant deck pages, with references the student can inspect.
- See a useful labeled example or diagram in an adjacent annotation area.
- Save the explanation and visual with that slide and restore them when returning.
- Attempt one application question and receive feedback on the reasoning.

The source deck is preserved. Additional background explanations are identified as supplemental. Slides alone cannot establish what the professor said or what will appear on an exam. Help is initiated by the student in this prototype.

Defer lecture recording, desktop-wide screen access, live overlays on other applications, Drive/Outlook integrations, mind maps, voice, and a full adaptive study scheduler until evidence supports their priority.

Before participant sessions, exercise the complete flow with the founder's material: navigate, ask, inspect references, view a visual, answer a question, change slides, return, and reload to check saved state. Check explanations and question answers against course material or an appropriate authoritative reference. Record unresolved errors rather than claiming correctness.

Deliverable: one working study interaction on real course material. A mock interface alone does not validate tutoring.

## Research step 3: compare and observe return

Recruit up to five students for the pilot, including the initial participants when suitable. Test the founder's session first, then classmates' sessions. The founder's preference is useful design feedback but is not independent demand evidence.

For a practical comparison, each student studies two different sections of similar difficulty: one using their normal workflow, including ChatGPT, and one using StudyBuddy. Alternate which tool goes first across participants. Avoid teaching the same topic twice and mistaking familiarity for a product advantage.

Capture:

| Observation | Purpose |
| --- | --- |
| Time and manual steps before a useful explanation | Assess whether the workflow reduces effort |
| Unassisted application answer after each section | Check understanding beyond perceived clarity |
| Incorrect explanations or unsupported course claims | Identify reliability failures |
| A different application question the following day, where feasible | Get an early retention signal |
| Which tool they choose for a subsequent study session and why | Test preference in actual use |

Offer access for their next lecture. Keep reminder-assisted sessions separate from voluntary returns. A small, informal comparison is directional evidence; topic difficulty and prior knowledge can confound results.

## Decision after the pilot

- Continue if several students independently encounter the same obstacle and choose to reuse the prototype because it solves that obstacle. Three of five voluntary returns is a useful initial target, not a universal benchmark.
- Revise if the workflow helps but explanations, visuals, or interaction details repeatedly fail.
- Reconsider the proposed difference if students find their existing ChatGPT workflow equally easy and consistently choose it again.
- After repeat use, present a specific paid offer and record actual commitments separately from hypothetical willingness to pay. Set the price and terms before making that offer.

## Immediate next actions

Founder: review the working product flow and recruit the first three conversations. No messages have been sent on the founder's behalf.

Assistant: validate the live local tutor, then iterate on the product using observed study sessions. The initial teaching flow has not been validated for learning benefit. The current delivery scope and dated checkpoints are in `docs/mvp-release-plan.md`, targeting October 18, 2026.
