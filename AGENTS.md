# Instructions for AI agents working in this repository

This is a QA/testing toolkit. It contains task instructions ("skills") and Python helper
scripts (stdlib only, Python 3.8+, no pip installs needed). **Any AI agent working here —
not only Claude — must follow these rules.**

## Rule 1: When the user asks for a testing task, read the matching skill file FIRST and follow it exactly

| User wants | Read this file before doing anything |
|---|---|
| Test cases / test scenarios from a requirement | `.claude/skills/test-cases/SKILL.md` |
| Report a bug / write a defect ticket | `.claude/skills/bug-report/SKILL.md` |
| A test plan or test strategy | `.claude/skills/test-plan/SKILL.md` |
| Test an API / check endpoints | `.claude/skills/api-test/SKILL.md` |
| Automate tests (Playwright/Maestro/Appium) | `.claude/skills/automate/SKILL.md` |
| Test data / dummy data files | `.claude/skills/test-data/SKILL.md` |
| Exploratory testing ideas | `.claude/skills/exploratory/SKILL.md` |
| Test summary / status report | `.claude/skills/test-report/SKILL.md` |
| Test the mobile app (Android/iOS) | `.claude/skills/mobile-test/SKILL.md` |

Each skill file contains a mandatory step-by-step workflow. Do not improvise your own
format — the workflows exist because their output formats are machine-validated.

## Rule 2: Never do by hand what a script does deterministically

Run these instead of generating the result yourself:

- `python .claude/skills/test-data/scripts/generate_data.py` — generates test data files
- `python .claude/skills/test-report/scripts/make_report.py` — computes report stats and the release verdict (NEVER calculate percentages or decide go/no-go yourself)
- `python .claude/skills/api-test/scripts/run_api_tests.py` — executes API test suites (it blocks production URLs by design; never add `--allow-any-env` without explicit user confirmation)
- `python .claude/skills/mobile-test/scripts/collect_evidence.py` — collects Android bug evidence (device info, screenshot, crash logs) via adb

Run each script with `--help` (or no args) to see usage.

## Rule 3: Validate your own output before showing it to the user

After writing a bug report or test cases, you MUST run the matching validator and fix
every ERROR it prints, repeating until it prints OK:

```
python .claude/skills/bug-report/scripts/validate_bug_report.py <your-file.md>
python .claude/skills/test-cases/scripts/validate_test_cases.py <your-file.md>
```

Never show the user an unvalidated file. Exit code 0 = acceptable.

## Rule 4: File locations

Write outputs to these folders (create if missing): `bug-reports/`, `test-cases/`,
`test-plans/`, `test-data/`, `api-tests/`, `reports/`, `evidence/`.

## Rule 5: Safety

- Never run tests against production environments without explicit user confirmation.
- Never print full auth tokens — mask them (`eyJhb...****`).
- No destructive operations (DELETE requests, `adb shell pm clear`, deleting data) without explicit approval.
- Never generate real personal data; use `@example.com` emails and official test card numbers only.
