---
name: test-plan
description: Create a full test plan or test strategy document for a feature, release, or project. Use when the user asks for a test plan, test strategy, or QA planning for a release.
---

# Test Plan Builder

Create a practical test plan document. Ask the user first (briefly, max 3 questions) about: what is being tested, the deadline/timeline, and the team size — unless they already said.

## Document structure

Write the plan as a markdown file in the project (e.g. `test-plans/<feature>-test-plan.md`) with these sections:

1. **Overview** — what is being tested, in 2-3 sentences
2. **Scope** — In scope / Out of scope (explicit lists)
3. **Test Approach** — which test types apply: functional, regression, API, UI, cross-browser/device, performance, security, accessibility. For each, say *why* it applies or is skipped.
4. **Entry / Exit Criteria** — when testing starts, when it's done (e.g. "all P1/P2 defects fixed, 95% test cases executed")
5. **Test Environment & Data** — environments, accounts, test data needs
6. **Risks & Mitigations** — realistic risks (tight timeline, unstable environment, missing requirements)
7. **Schedule & Estimates** — rough phases with effort
8. **Deliverables** — test cases, defect reports, summary report

Keep it lean — a plan people will actually read (1-2 pages), not a 20-page template. Mark anything you assumed with `(assumption)` so the tester can confirm with the team.
