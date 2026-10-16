# StudyBuddy product baseline

Version 0.2 · October 16, 2026 · Working documents for founder review

These documents are the starting point for product decisions. They preserve the long-term idea while keeping the next release focused on a useful, reliable study session. They describe a product in development; they do not declare the MVP complete.

| Document | Question it answers | Authority |
| --- | --- | --- |
| [Product vision](vision.md) | Why does StudyBuddy exist, and where should it go? | Long-term direction and principles |
| [Product requirements / PRD](prd.md) | What must we build, and what counts as finished? | Requirements, scope, acceptance criteria, and release gates |
| [Marketing requirements / MRD](mrd.md) | Who needs this, what do they value, and how do we reach them? | Customer hypotheses, positioning, and market validation |
| [Competitive analysis](competitive-analysis.md) | What can students use instead, and what must we prove? | Sourced comparisons, metrics, and research gaps |
| [Product roadmap](roadmap.md) | What happens now, next, and later? | Sequence and conditional delivery windows |

## Confirmed constraints and current state

- Use free resources and open-source components. No paid inference APIs, subscriptions, or paid hosting are authorized. Existing hardware and electricity still have costs.
- Target a usable personal MVP by **Sunday, October 18, 2026**, using America/New_York dates. This is a target subject to the PRD gates, not a promised public launch.
- First target machine: the founder's M3 Pro Mac with 18 GB memory. Mac execution and performance are unverified.
- Primary experience: a Mac menu-bar companion following the active study window across apps, clarified by the founder on October 16. Native behavior is not yet Mac-validated.
- The supporting PDF workspace and local model connection work in the cloud checkout. Real tutor checks failed on answer quality. See the [validation record](../validation.md).
- The founder reports a personal study problem and access to 5–10 classmates. No independent customer trial, retention result, willingness to pay, or market share has been established.

## Evidence labels

- **Observed:** inspected implementation or a recorded test; the environment and limits must be stated.
- **Founder-reported:** information from the founder, not an independent customer finding.
- **Source-verified:** a retrieved primary source; vendor documentation is a claim about its product, not our hands-on benchmark.
- **Hypothesis / proposed target:** a decision to test, not a fact or achieved result.
- **Unverified:** research or execution has not established the claim.

## Keeping the documents aligned

Before implementation, connect the task to a PRD requirement ID and a roadmap phase. For a new feature, record the student problem, evidence, cost/license implications, acceptance check, and what it would replace in the current scope. Put ideas without that evidence into roadmap discovery instead of silently adding them to the MVP.

Update the PRD when requirements change, the roadmap when order or dates change, and the validation record when evidence changes. Update the MRD and competitive analysis after customer research or a new source check. Record meaningful changes in the table below. The founder owns priorities and user research; Codex maintains implementation and test records during active work. No background execution or outreach is implied.

The repository's [agent instructions](../../AGENTS.md) carry this workflow into future development sessions. They do not create an extra approval process.

The numerical acceptance and pilot targets introduced in version 0.1 are proposed working defaults. The founder has not separately approved those thresholds. They make tradeoffs reviewable and should be adjusted explicitly, not represented as measured outcomes.

## Change log

| Date | Decision | Reason / effect |
| --- | --- | --- |
| 2026-10-16 | Prepared native shell and shared companion alpha | Eighteen shared tests, production build and simulated native UI flow passed; native macOS compilation/capture, broad context identity, tutor quality and speed remain open |
| 2026-10-16 | Follow the active window automatically across apps | Founder uses Canvas and rejected per-app/window selection. Optional PDF attachment adds context; screenshots do not include video audio/transcripts or off-screen content |
| 2026-10-16 | Restored the integration-first scope: FR-12/13/14 are P0 | Founder requires menu-bar activation and help following the lecture in another app. Reuse the workspace engine; prioritize native shell and window following over workspace polish or broader model benchmarking. Direct drawing over external content remains deferred; accuracy gates remain open |
| 2026-10-16 | Completed the expanded model screen; retained alpha status | New model still has critical errors; added one-command startup, failure preservation and Mac acceptance instructions |
| 2026-10-15 | Established the five-document baseline | Avoid disconnected feature work and inconsistent definitions of completion |
| 2026-10-15 | Kept October 18 as the personal MVP target; gated wider pilot access on reliability | Live tutoring failures make a connection-health check insufficient for release |
| 2026-10-15 | Made the PRD authoritative over older overlapping plans | The [first experiment](../first-week-plan.md) remains a research protocol; the [week plan](../mvp-release-plan.md) becomes an execution checklist |
| 2026-10-15 | Marked commercial competitor pricing and share unverified | Environment proxy denied those websites; no numbers were guessed |

The [implementation README](../../README.md), [Mac setup](../mac-setup.md), and [open-source stack](../open-source-stack.md) remain operational references. Committing these documents and the alpha source does not establish a completed MVP or a tested Mac build. The PRD release gates remain open.
