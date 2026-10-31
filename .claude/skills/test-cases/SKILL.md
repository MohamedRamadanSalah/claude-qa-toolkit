---
name: test-cases
description: Generate a complete set of test cases from a requirement, user story, screenshot, or feature description. Covers positive, negative, boundary, and edge cases, and validates its own output with a script. Use when the user asks to write, design, or generate test cases or test scenarios.
---

# Test Case Generator

You are helping a QA tester design test cases. Follow this workflow EXACTLY — do not skip steps.

## Workflow (mandatory)

1. **Understand the input.** If the requirement is missing key facts (expected behavior, user roles, field limits), ask 1-2 short questions. Otherwise proceed.
2. **List the testable behaviors** first as a short bullet list (this is your checklist — every behavior must get test cases).
3. **Write the test cases to a file** named `test-cases/<feature-name>.md` using EXACTLY this table format — same columns, same order, nothing added or removed:

```
| ID | Category | Title | Preconditions | Steps | Test Data | Expected Result | Priority |
|---|---|---|---|---|---|---|---|
| TC-001 | Positive | Login succeeds with valid credentials | User account exists and is active | 1. Open login page<br>2. Enter valid email<br>3. Enter valid password<br>4. Click Login | user1@test.com / Pass123! | User lands on dashboard; welcome message shows the user's name | P1 |
```

   Rules for each cell:
   - **ID**: `TC-001`, `TC-002`, ... sequential, no duplicates.
   - **Category**: exactly one of `Positive`, `Negative`, `Boundary`, `Edge`, `Non-functional`.
   - **Steps**: numbered `1. 2. 3.`, separated with `<br>` inside the cell. Precise enough that a junior tester needs zero questions.
   - **Expected Result**: the exact observable outcome. NEVER "works", "success", "no error".
   - **Priority**: `P1` (critical) / `P2` (major) / `P3` (minor).
   - Required coverage: at least one `Positive`, one `Negative`, one `Boundary` case. Add `Edge` cases (interruption, concurrency, unicode/Arabic text, double-submit) whenever the feature has input or state.

4. **Validate your output (MANDATORY):**

```
python .claude/skills/test-cases/scripts/validate_test_cases.py test-cases/<feature-name>.md
```

   If the validator prints any `ERROR`, fix the file and run it again. Repeat until it prints `OK`. Never show the user an unvalidated file.

5. **Finish** by showing the user: the coverage counts the validator printed, plus a short "Coverage gaps / questions for the team" section listing anything ambiguous in the requirement.

If the user asks for CSV/Excel/TestRail format, first produce and validate the markdown version, then convert.
