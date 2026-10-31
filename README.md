# Claude QA Toolkit

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![Claude Code](https://img.shields.io/badge/Claude%20Code-skills-D97757)
![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)

Nine Claude Code skills for QA engineers: test cases, bug reports, test plans, API tests,
automation, test data, exploratory charters, test reports and mobile testing. Each one is backed
by validator scripts, so the AI's output is checked before you see it.

## Quick start

```bash
git clone https://github.com/MohamedRamadanSalah/claude-qa-toolkit
cd claude-qa-toolkit
claude            # the skills in .claude/skills/ load automatically
```

Then type a skill name as a slash command, for example `/bug-report`, or just describe the task.
To use the skills in every project, copy the folders in `.claude/skills/` into `~/.claude/skills/`.

**Design principle:** each skill ships with Python scripts (stdlib only — no installs needed)
that do the precise work deterministically. The AI writes the content; the scripts
**generate data, run tests, compute stats, and validate the AI's output**. If a validator
finds errors, the skill forces the AI to fix them before showing you anything. This keeps
quality high even with smaller/faster AI models.

Requirements: Python 3.8+ in PATH. Optional: `adb` for `/mobile-test`, Playwright or pytest for `/automate`.

👉 **New here? Read [TESTER-GUIDE.md](TESTER-GUIDE.md)** — it explains which skill to use when,
with copy-paste example prompts and the full bug-report flow step by step.

**Works beyond Claude too:** the Python scripts run anywhere, and [AGENTS.md](AGENTS.md)
teaches other AI tools (Cursor, Codex, Gemini CLI...) to follow the same skills and validators.
Slash commands and auto-triggering are Claude Code features; in other tools, ask the AI to
"read AGENTS.md and then do <task>".

## Custom skills (in `.claude/skills/`)

| Command | What it does |
|---|---|
| `/test-cases` | Generates full test cases (positive, negative, boundary, edge) from a requirement or user story |
| `/bug-report` | Turns a rough bug description or screenshot into a professional Jira-ready bug report |
| `/test-plan` | Builds a lean, practical test plan document for a feature or release |
| `/api-test` | Builds and runs API requests, or generates a whole API test suite from a Swagger spec |
| `/automate` | Converts manual test cases into Playwright / pytest automated tests |
| `/test-data` | Generates realistic test data files (CSV/JSON/SQL) including edge-case values |
| `/exploratory` | Creates exploratory testing charters — creative ideas for where bugs hide |
| `/test-report` | Writes a test summary report with pass/fail stats and a go/no-go recommendation |
| `/mobile-test` | Tests mobile apps — drives Android devices via adb (install builds, screenshots, crash logs), mobile-specific test cases, Maestro/Appium automation |

## Bundled scripts (what makes the skills accurate)

| Script | Skill | What it guarantees |
|---|---|---|
| `validate_test_cases.py` | test-cases | Table format, sequential TC-IDs, no vague "works" results, coverage of Positive+Negative+Boundary |
| `validate_bug_report.py` | bug-report | All required sections present, specific title, valid severity/priority, numbered repro steps, Actual ≠ Expected |
| `run_api_tests.py` | api-test | Executes suites, checks status/JSON/timing, detects leaked stack traces, **refuses to run against production URLs** |
| `make_report.py` | test-report | All percentages and the go/no-go verdict computed by fixed rules — the AI can never miscalculate or sugar-coat |
| `generate_data.py` | test-data | Reproducible datasets (CSV/JSON/SQL) with built-in edge-case rows (unicode, Arabic, injection strings, boundary numbers, invalid dates) |
| `collect_evidence.py` | mobile-test | One command: device info + screenshot + error logs + parsed crash stack traces from a connected Android device |

Every script can be run by hand too — each prints usage help when run with wrong arguments.

## Useful built-in Claude Code skills

| Command | What it does |
|---|---|
| `/code-review` | Reviews code changes for bugs — great when testing a developer's PR |
| `/security-review` | Security review of pending changes |
| `/verify` | Verifies a code change actually works end-to-end |
| `/review` | Reviews a GitHub pull request |

## Tips

- You can paste screenshots directly into Claude Code (Ctrl+V) — useful with `/bug-report` and `/test-cases`.
- You can drop files (Swagger spec, Excel requirements, logs) into this folder and ask Claude to read them.
- Skills also trigger automatically — e.g. saying "I found a bug where..." will use the bug-report skill.

## License

[MIT](LICENSE) © 2026 Mohamed Ramadan
