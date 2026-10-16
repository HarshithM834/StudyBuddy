# StudyBuddy working context

For product or feature work, start with `docs/product/README.md`, then the relevant requirements in `docs/product/prd.md` and phase in `docs/product/roadmap.md`. These documents are the working baseline; `docs/validation.md` records what actually passed or failed.

- Map feature work to a PRD requirement and roadmap phase. For a scope change, update the affected documents and the baseline change log so the change stays visible.
- Treat the documents as a coordination aid, not a new permission process. The user's current instructions take precedence. Make ordinary authorized fixes without stopping for document approval.
- Primary product: a native Mac menu-bar companion floating beside and following the active window across apps during explicit study mode (FR-12/13/14). The PDF workspace is supporting infrastructure, not the main user flow.
- Use free resources and open-source components. Do not add a paid inference adapter, paid service dependency, or automatic paid fallback. Future product pricing remains undecided.
- Preserve the distinction between implemented behavior, measured results, founder reports, hypotheses, and unverified claims. Local model health is not evidence of correct tutoring; a working Linux run is not a verified Mac run.
- The initial target is an M3 Pro Mac with 18 GB memory. October 18, 2026 is the founder MVP target subject to the PRD release gates; dates are America/New_York.
- Keep course uploads, personal notes, conversations, model weights, and credentials out of version control. Preserve existing local work during tests.
- Focus on building and validating the product. Do not turn development discussions into unsolicited subject lectures.

The root README contains setup/check commands. Do not run inference benchmarks or the full application test suite for documentation-only edits; check document links, claims, and generated artifacts instead.
