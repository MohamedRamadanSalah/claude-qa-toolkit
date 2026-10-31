# 📘 Tester Guide — How to Use Claude Code for QA Work

This guide explains **which skill to use, when to use it, and exactly what happens** when you use it.
Written in simple English. Just copy the example prompts and change them for your work.

---

## 🚀 Getting Started (one time only)

1. Clone this repo and open a terminal in its folder:
   `git clone https://github.com/MohamedRamadanSalah/claude-qa-toolkit && cd claude-qa-toolkit`
2. Start Claude Code by typing: `claude`
3. That's it. The skills load automatically because they live in `.claude/skills/` in this folder.

**Important:** always start Claude Code from THIS folder, or the skills will not be available.

---

## 🧭 Which skill do I use? (quick decision table)

| Your situation | Use this | Example prompt |
|---|---|---|
| "I got a new user story / requirement to test" | `/test-cases` | `/test-cases here is the story: user can reset password by email...` |
| "I found a bug and need to report it" | `/bug-report` | `/bug-report the app freezes when I upload a photo bigger than 10MB` |
| "New feature/release is coming, I need to plan testing" | `/test-plan` | `/test-plan we release the new checkout feature on July 20` |
| "I need to test the backend API" | `/api-test` | `/api-test here is the swagger: https://qa.myapp.com/swagger.json` |
| "I'm tired of repeating the same manual tests" | `/automate` | `/automate convert my login test cases to Playwright` |
| "I need fake users/orders to test with" | `/test-data` | `/test-data give me 100 users as CSV` |
| "New feature, no test cases yet, where do I start hunting bugs?" | `/exploratory` | `/exploratory the new chat feature, messages + attachments` |
| "My manager wants the testing status" | `/test-report` | `/test-report total 120, passed 100, failed 15, blocked 5...` |
| "I'm testing the mobile app" | `/mobile-test` | `/mobile-test install this build and check the login screen` |

💡 You don't have to type the slash command — if you just say *"I found a bug where..."*, Claude understands and uses the right skill automatically. The slash command just makes it certain.

---

## 🐞 How a bug report is generated (step by step)

This is the most important daily flow. Here is exactly what happens:

### You type something rough — even one line:

> *"when i click save button two times the order created two times"*

### Claude then does this automatically:

```
Step 1  EXTRACT   Claude reads your words, any screenshot you pasted,
                  and any log you gave. It pulls out: steps, error text, environment.

Step 2  ASK       If something important is missing (which build? which browser?),
                  Claude asks you ONE short question. If you're busy, it uses
                  placeholders like <build version> that you fill later.

Step 3  WRITE     Claude writes the full report to a file:
                  bug-reports/duplicate-order-double-click.md
                  with ALL sections: Title, Environment, Severity, Priority,
                  Steps to Reproduce, Actual Result, Expected Result,
                  Reproducibility, Attachments, Notes.

Step 4  VALIDATE  Claude runs the Python checker on its own report:
                  python .claude/skills/bug-report/scripts/validate_bug_report.py ...
                  The checker REJECTS bad quality: vague titles like "Login broken",
                  missing sections, "Actual = Expected", steps not numbered.
                  Claude must fix every ERROR and run the check again until it prints OK.

Step 5  SHOW      You get the final report + one line explaining why Claude chose
                  that Severity/Priority. Copy-paste it into Jira / Azure DevOps. Done.
```

### Example — what you get from that one rough line:

```
**Title:** [Orders] Duplicate order created when Save is double-clicked

**Severity:** Major        **Priority:** P2

**Steps to Reproduce:**
1. Open the new order page and fill all required fields
2. Click the Save button twice quickly (within ~1 second)

**Actual Result:** Two identical orders are created with different order IDs.
**Expected Result:** Only one order is created; the button disables after first click.

**Reproducibility:** Always (tested 5 out of 5 tries)
```

### 📱 Bug on the mobile app? Even easier:

Connect the phone by USB and just say: **"the app crashed"**. Claude runs the evidence collector:

```
python .claude/skills/mobile-test/scripts/collect_evidence.py --package com.yourapp
```

One command collects: device model + Android version, a screenshot, the error logs, and the **crash stack trace** — then writes the bug report for you with all of it included. You attach the `evidence/` folder to the ticket.

---

## 📋 The other skills — what happens when you use them

### `/test-cases` — writing test cases
1. Paste the requirement/user story (or a screenshot of the screen).
2. Claude lists the behaviors it will cover, then writes a table to `test-cases/<feature>.md` with categories: **Positive, Negative, Boundary, Edge, Non-functional**.
3. A Python validator checks the file: IDs correct, no vague "works" results, at least one Negative and one Boundary case. Claude must fix errors before showing you.
4. You get the table + a list of open questions to ask your team (things the requirement didn't say).

### `/api-test` — testing APIs
1. Give the base URL + token + the endpoints (or a Swagger link).
2. Claude writes a test suite file `api-tests/<name>.json` covering: valid requests, missing fields, no token (401), wrong role (403), missing IDs (404), boundary values.
3. The Python runner executes everything and prints a pass/fail table.
4. **Safety:** the runner REFUSES to run if the URL doesn't look like a test environment — it will never accidentally hit production.
5. For every real failure, ask Claude: *"write bug reports for the failures"* — it chains into the bug-report flow.

### `/test-report` — status report for your manager
1. Give your numbers: total, passed, failed, blocked + list of open defects.
2. Claude puts them in `reports/results.json`, and a Python script computes ALL percentages and the verdict with fixed rules:
   - Open Blocker/Critical bug → ❌ **NOT READY**
   - Less than 90% executed → ❌ **NOT READY**
   - Failure rate over 10%, or open Major → ⚠️ **RELEASE WITH RISK**
   - Otherwise → ✅ **READY TO RELEASE**
3. The script also catches wrong math (e.g. passed+failed more than total) and asks you to correct it.
4. Claude adds a short executive summary on top. Ask for an HTML version if you want something pretty to share.

### `/test-data` — fake data for testing
1. Say what you need: *"50 users as CSV"* or *"20 orders as SQL inserts"*.
2. A Python generator creates the file in `test-data/` — same command always gives the same data (reproducible).
3. **Bonus:** it automatically adds edge-case rows marked in a `_note` column: empty values, 255/256-character strings, Arabic text, emojis, `' OR 1=1 --`, invalid dates like Feb 30. Import these to test that the app doesn't break.

### `/exploratory` — bug hunting ideas
Describe the feature and you get 3-6 timed "charters" — creative missions like *"cancel every operation in the middle"*, *"open the same record in two tabs"* — plus Claude's top 3 guesses for where this specific feature will break.

### `/automate` — turning manual tests into automated
Give your manual test cases. Claude writes Playwright (web) or Maestro (mobile) tests, **runs them**, and shows you the results. It follows good rules automatically: no fixed sleeps, stable selectors, independent tests.

### `/test-plan` — planning a release
Answers 3 quick questions (what, when, who), then writes a short practical plan to `test-plans/` — scope, approach, entry/exit criteria, risks. 1-2 pages people actually read, with assumptions marked for you to confirm.

---

## 🔓 No code access? No problem (black-box testing)

You do NOT need the project's source code for any skill here. This is the normal tester
situation — you test what the users get, not the code.

### You only have a web link

| Goal | How |
|---|---|
| Test cases, exploratory, bug reports | Work from requirements + what you see on screen — no code was ever needed |
| Test the API (no Swagger, no docs) | Open the site, press **F12 → Network tab**, use the app normally. Every API call appears there. Right-click a request → **Copy as cURL** → paste it to Claude and say *"build an api-test suite from this"* |
| See why a page is broken | F12 → **Console tab** — copy the red errors and paste them into `/bug-report` |
| Automate the UI | Say *"automate the login flow on https://qa.myapp.com"* — Playwright drives any live site by URL; Claude can open the page and find the buttons itself |

### You only have an APK file

```
adb install -r app.apk                  # install it on the device/emulator
adb shell pm list packages -3           # find the app's package name (needed for evidence collector)
```

After that, EVERYTHING in `/mobile-test` works: screenshots, crash logs, the evidence
collector, Maestro automation — they all read from the *running app*, not the source code.
If install fails, tell Claude the exact error (common: wrong CPU type, min Android version,
signature conflict with an older installed version — uninstall it first).

### What you genuinely cannot do without code
Only developer-side things: reviewing code changes, unit tests, fixing bugs. That's not
the tester's job — everything you need for finding and reporting bugs is black-box.

---

## 📅 A typical day with the toolkit

```
09:00  New story in the sprint        →  /test-cases  (paste the story)
10:30  Testing, found something odd   →  "I found a bug where..."  → validated report → Jira
13:00  Need data for the test env     →  /test-data 50 users CSV
14:00  Backend team says API is ready →  /api-test with the swagger link
16:30  Manager asks "are we ready?"   →  /test-report with today's numbers
```

## 💡 Tips

- **Paste screenshots** (Ctrl+V) — Claude reads them. A screenshot of an error + one sentence = a full bug report.
- **Drop files in this folder** (Swagger JSON, requirements Excel, logcat dump) and say *"read requirements.xlsx and write test cases"*.
- **Everything is saved as files** (`bug-reports/`, `test-cases/`, `reports/`...) — nothing gets lost when the chat ends.
- **Don't trust, verify:** every skill validates its own output with Python scripts. If you ever see a low-quality report, tell Claude *"run the validator"*.
- If a skill doesn't trigger, type its slash command directly: `/bug-report`, `/test-cases`, etc.
- New session = fresh start. Old files are still there; just tell Claude *"continue from test-cases/login.md"*.
