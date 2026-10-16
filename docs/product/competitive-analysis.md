# Competitive analysis

Version 0.1 · Evidence snapshot: October 15, 2026 · [Product baseline](README.md)

## Conclusion for product decisions

StudyBuddy enters an established space. The founder and classmates already use ChatGPT with course material. Verified open-source alternatives also offer local document chat and source citations. “AI that reads your notes” and “runs locally” are insufficient as stand-alone differentiation.

The advantage to test is a reliable study session attached to the actual lecture: less context setup, saved explanations and visuals at the relevant slide, and feedback that helps the student apply the idea. Our current tutor has failed that reliability test. This analysis does not conclude that StudyBuddy is superior to any competitor.

## Research coverage and limitations

Two open-source projects' official READMEs, license files, and GitHub repository pages were retrieved and reviewed. Those document advertised capabilities and observable repository metrics; neither product was installed or benchmarked in this analysis.

The environment proxy returned `403 Forbidden` while connecting to official commercial product/pricing pages for ChatGPT, NotebookLM, StudyFetch, Knowt, RemNote, and Quizlet. Current feature availability, prices, usage limits, customer counts, and commercial market share were therefore **not verified**. The commercial rows below are a background shortlist and research agenda, not a refreshed feature audit. No alternate proxy was used to evade the restrictions.

## Alternatives and practical tradeoffs

| Alternative | What is established / evidence level | Strength relevant to the student | Weakness or tradeoff to investigate | Consequence for StudyBuddy |
| --- | --- | --- | --- | --- |
| ChatGPT + course files | Founder reports personal use and classmates' use with slides/assignments. General assistant capabilities are background knowledge; current Study Mode/features/limits unverified [C1] | Already in the students' workflow; broad conversational help | Measure the actual effort to supply/recover the right course context and resume work. Do not assume it cannot cite sources, teach step by step, or quiz | Primary comparison; show a workflow benefit beyond another chat box |
| Google NotebookLM | Background: source-oriented research/study assistant. Current capabilities and limits unverified [C2] | Direct conceptual overlap with asking questions about supplied material | Verify slide navigation, source/annotation persistence, practice flow, privacy terms, and device requirements hands-on | Source grounding alone is not a defensible differentiation claim |
| StudyFetch | Background: dedicated AI study-tool category; current offering unverified [C3] | Competes for the same study session and student attention | Verify the actual upload → tutor → practice loop, access limits, and correctness on the same material | Do not position notes or quizzes as unique features without a current comparison |
| Knowt | Background: study notes/flashcards/practice category; current offering unverified [C4] | Relevant to students seeking study material and practice | Verify which features are free, supported source formats, and quality of reasoning feedback | Test the value of understanding a specific slide, not just generating more study content |
| Quizlet | Background: flashcard and practice category; current AI and plan details unverified [C5] | Familiar practice-oriented alternative | Test conceptual explanation, course-source traceability, and transfer to a new problem; no claim that these are absent | StudyBuddy must help with application as well as recall |
| RemNote | Background: connected notes and spaced-repetition category; current plans/features unverified [C6] | Close to the long-term notes-to-practice vision | Verify PDF study flow, setup effort, and any AI service dependency/limits | Avoid expanding into a general notes system without evidence of a gap |
| Open Notebook | **Source-verified:** MIT source; source/context chat, citations, source organization, local-model support, and podcast generation advertised [O1–O3] | Existing customizable foundation for source-grounded, local research | Documented Docker/database/model configuration adds setup steps; course pedagogy and per-slide workflow were not evaluated. Its support for cloud providers does not make every configuration free | Candidate to evaluate before rebuilding generic ingestion/retrieval; local privacy is not exclusive to us |
| AnythingLLM | **Source-verified:** MIT source; Mac/Windows/Linux desktop availability, document chat, citations, workspace memory, local/cloud model options, and agents advertised [A1–A3] | Broad advertised feature coverage and a desktop route; source code available for inspection | General document/agent scope may add complexity for a simple study task; not measured. README discloses telemetry and opt-out; external providers remain configuration-dependent | Compare its existing desktop document flow before investing in a custom desktop shell; reuse only after license/configuration review |
| Peers, office hours, videos, and search | Founder reports searching videos/web; peers are a reachable option | Human clarification and varied explanations can be valuable | Availability, search effort, and matching the professor's material vary; measure rather than assume | The product competes with ways of getting unstuck, not only software brands |

“Not evaluated” does not mean “missing.” Weakness hypotheses require hands-on testing. Vendor comparison tables are not independent evidence about their rivals, so Open Notebook's claims about NotebookLM were not used as verified facts.

## Observable rival metrics

| Product | Metric observed on October 15, 2026 | What it measures | What it does not establish |
| --- | --- | --- | --- |
| Open Notebook | **40,218 GitHub stars; 4,658 forks** [O3] | Repository interest and fork activity at retrieval | Active students, paid customers, learning quality, revenue, or market share |
| AnythingLLM | **67,148 GitHub stars; 7,506 forks** [A3] | Repository interest and fork activity at retrieval | Active students, paid customers, learning quality, revenue, or market share |
| ChatGPT, NotebookLM, StudyFetch, Knowt, Quizlet, RemNote | Current student MAU, retention, paid conversion, and revenue not verified in this review | No comparable measurement established | A ranking by adoption or business performance |
| StudyBuddy | Eight API tests passed; nine recorded real-model requests exposed quality failures; no independent participant trials completed [S1] | Current engineering evidence and research status | Customer traction, educational effectiveness, or a competitive accuracy score |

Stars and forks are separate, overlapping, non-customer measures. They must not be added together, compared with a commercial app's user count, or used as a denominator for a share chart. Repository popularity is not a reason by itself to adopt a dependency.

## Market share

**No defensible percentage share for the target market is established.** No common denominator, geographic scope, time window, or comparable student-usage counts were found in the sources reviewed. This is a research gap, not a claim that the companies have no users or that such data cannot exist.

For a future study, define the category as active students in the chosen geography/course segment who used a study-assistance tool in the previous 30 days. Measure use of each alternative in that same sample and period. Students can use multiple products, so usage penetration can sum above 100%; label it that way rather than presenting an exclusive market-share pie chart. A primary-tool share requires a separate mutually exclusive question. Revenue share needs comparable category-specific revenue, which is unavailable here.

## Price and free-use comparison

| Alternative | Verified cost statement | Remaining verification |
| --- | --- | --- |
| Open Notebook | MIT source is available; README supports local model use as an alternative to provider API keys [O1/O2] | Complete all-local configuration, hardware requirements, and cost of optional features were not run |
| AnythingLLM | MIT source is available; README supports local models and a native embedder [A1/A2] | Verify desktop settings, model downloads, telemetry choice, and absence of paid-provider dependencies in the chosen configuration |
| Commercial alternatives | No current price or free-tier quota verified | Retrieve official plan pages, record currency, billing period, region, date, eligibility, and feature limits; distinguish a free tier from a temporary trial |
| StudyBuddy | Current implemented path uses local inference and has no paid-provider adapter [S1/S2] | Actual Mac performance/setup and future distribution costs; no “free forever” pricing commitment |

Do not publish stale dollar figures, assume student promotions apply, or describe an open-source tool's optional hosted AI calls as free.

## October 16 product clarification

The founder requires a menu-bar companion that follows slides in an existing lecture app. This is a workflow hypothesis to test against the alternatives above, not a verified exclusive feature. Compare activation effort, window/slide recognition, backtracking, interruption, and correct recovery as well as tutor accuracy. The existing PDF workspace is supporting infrastructure. Competitor feature checks and market-share gaps remain unchanged.

## Comparison protocol and next decisions

After PRD quality gates permit a trial, compare the same tasks and similar-difficulty material: import, find a confusing slide, ask a question, inspect support, save/return, attempt a new problem, and receive feedback. Record tool version/plan, hardware/network conditions, setup time, time to useful help, manual copying steps, answer/source errors, successful resumption, and the student's later tool choice.

The same human-reviewed correctness rubric must be used across tools. Keep instructor information and source access equivalent; do not compare StudyBuddy with a deliberately under-contextualized ChatGPT prompt. Alternate task order. Observe participants' existing tools or legitimately available free access; this is competitive research, not adoption of commercial products as StudyBuddy dependencies. This document does not authorize purchases or accounts requiring payment.

Priorities:

1. Fix StudyBuddy's correctness blockers before recruiting users to trust it.
2. Observe the actual ChatGPT workflow; it is the confirmed incumbent for this founder and reported classmates.
3. Evaluate NotebookLM and one dedicated study tool once current official access is available.
4. Evaluate Open Notebook or AnythingLLM for reusable components/workflows before replacing current infrastructure. No new dependency is adopted by this report.
5. Complete current commercial pricing/feature verification before making external comparative claims.

## Source register

Retrieved October 15, 2026 unless marked blocked. Repository files below use the commit identifiers observed on the corresponding GitHub pages; downloaded file hashes and retrieval outcomes are retained in [research-sources.json](research-sources.json). Metrics refer to the retrieved repository page, not a timeless property of a commit.

- **O1:** [Open Notebook README](https://github.com/lfnovo/open-notebook/blob/a0f6f3081ae06328f0a451b3a3ef2959ca25721d/README.md) — advertised functionality, providers, configuration steps.
- **O2:** [Open Notebook MIT license](https://github.com/lfnovo/open-notebook/blob/a0f6f3081ae06328f0a451b3a3ef2959ca25721d/LICENSE).
- **O3:** [Open Notebook repository](https://github.com/lfnovo/open-notebook) — star/fork snapshot from repository page data.
- **A1:** [AnythingLLM README](https://github.com/Mintplex-Labs/anything-llm/blob/7cbea8025211f7e7ead3701979157bd0d0e1f140/README.md) — advertised desktop, local providers, document chat, citations, and telemetry disclosure.
- **A2:** [AnythingLLM MIT license](https://github.com/Mintplex-Labs/anything-llm/blob/7cbea8025211f7e7ead3701979157bd0d0e1f140/LICENSE).
- **A3:** [AnythingLLM repository](https://github.com/Mintplex-Labs/anything-llm) — star/fork snapshot from repository page data.
- **S1:** [StudyBuddy validation record](../validation.md) — cloud checks, real-model errors, Mac validation gap.
- **S2:** [StudyBuddy open-source stack](../open-source-stack.md) — current dependencies and license notes.
- **C1, blocked verification targets:** [ChatGPT Study Mode](https://openai.com/index/chatgpt-study-mode/) and [pricing](https://chatgpt.com/pricing/).
- **C2, blocked verification target:** [NotebookLM](https://notebooklm.google/).
- **C3, blocked verification target:** [StudyFetch](https://www.studyfetch.com/).
- **C4, blocked verification target:** [Knowt](https://knowt.com/).
- **C5, blocked verification target:** [Quizlet features](https://quizlet.com/features).
- **C6, blocked verification target:** [RemNote pricing](https://www.remnote.com/pricing).

The C-links are research targets, **not citations establishing current product claims**. The report is usable for internal prioritization now; current commercial comparisons require a further source check before external use.
