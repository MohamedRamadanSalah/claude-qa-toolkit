---
name: test-report
description: Create a test summary / test execution report from results — pass/fail stats, defect summary, and a go/no-go verdict computed by script (never by guessing). Use when the user needs a test report, daily QA status, or release sign-off summary.
---

# Test Report Writer

All math and the release verdict are computed by a Python script — NEVER calculate percentages or decide go/no-go yourself. Follow this workflow EXACTLY.

## Workflow (mandatory)

1. **Collect the numbers** from the user: total test cases, passed, failed, blocked, and the list of defects (id, severity, status, title). If numbers are missing, ask for them — do not invent.
2. **Write the input file** `reports/results.json`:

```json
{
  "project": "MyApp v2.3",
  "date": "<today>",
  "total": 120, "passed": 100, "failed": 12, "blocked": 3,
  "defects": [
    {"id": "BUG-101", "severity": "Critical", "status": "Open", "title": "Login crash on timeout"}
  ],
  "notes": "optional context from the tester"
}
```

   Severity: `Blocker|Critical|Major|Minor|Trivial`. Status: `Open|Fixed|Deferred`.

3. **Generate the report:**

```
python .claude/skills/test-report/scripts/make_report.py --in reports/results.json --out reports/test-report.md
```

   - If the script prints `INPUT ERRORS` (e.g. passed+failed+blocked > total), tell the user exactly what is inconsistent and ask for the correct numbers. NEVER silently adjust numbers to make them fit.
   - The script computes the verdict with fixed rules: open Blocker/Critical → ❌ NOT READY; execution < 90% → ❌; failure rate > 10% or open Major → ⚠️ RELEASE WITH RISK; otherwise ✅ READY. Do not override the verdict; if the user disagrees, they can change the input data.

4. **Add the human part** (this is YOUR job, after the script): edit the generated report to add a 2-3 sentence executive summary at the top, and a "Risks & blockers" section based on what the user told you. Never soften bad news.
5. Offer to also produce a polished HTML version (Artifact) for sharing with managers.
