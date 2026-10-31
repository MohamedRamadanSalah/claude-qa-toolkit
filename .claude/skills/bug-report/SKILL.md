---
name: bug-report
description: Turn a rough description of a problem, error log, or screenshot into a professional, validated bug report ready to paste into Jira/Azure DevOps. Use when the user found a bug, wants to report a defect, or needs help writing a bug ticket.
---

# Bug Report Writer

The user is a tester who found a bug. They may describe it roughly, in broken English, or just paste an error/screenshot. Produce a complete, professional bug report. Follow this workflow EXACTLY.

## Workflow (mandatory)

1. **Extract facts** from what the user gave (steps, environment, exact error text, screenshots — Read any image they attached).
2. If reproduction steps or environment are missing, ask ONE short question covering all gaps. If the user seems in a hurry, use placeholders like `<build version>` and mark them clearly.
3. **Write the report to a file** `bug-reports/<short-slug>.md` using EXACTLY this template (keep every `**Section:**` header — the validator checks them):

```
**Title:** [Component] What fails + under which condition

**Environment:** OS / browser or device / app version / build / environment (QA, staging...)

**Severity:** Blocker | Critical | Major | Minor | Trivial
**Priority:** P1 | P2 | P3

**Preconditions:** state needed before the steps

**Steps to Reproduce:**
1. ...
2. ...

**Actual Result:** what actually happens — include the EXACT error text

**Expected Result:** what should happen, with requirement reference if known

**Reproducibility:** Always / Intermittent (x out of y tries)

**Attachments/Evidence:** screenshots, logs, video to attach

**Notes / Possible cause:** optional observations
```

   Severity guide: Blocker = testing/usage cannot continue; Critical = major function broken, no workaround; Major = major function broken but workaround exists; Minor = small function/UI defect; Trivial = cosmetic.

4. **Validate your report (MANDATORY):**

```
python .claude/skills/bug-report/scripts/validate_bug_report.py bug-reports/<short-slug>.md
```

   Fix every `ERROR` and re-run until it prints `OK`. Try to fix `WARN` lines too. Never show the user an unvalidated report.

5. **Show the user** the final report plus one line justifying the Severity/Priority you chose.

Rules: title must be specific and searchable ("Login button does nothing after session timeout on Chrome 126" — never "Login broken"). Facts only, no blame, no guesses stated as fact.
