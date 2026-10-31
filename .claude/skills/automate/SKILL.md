---
name: automate
description: Convert manual test cases into automated tests (Playwright for UI, pytest/requests for API) and help build or extend a test automation framework. Use when the user wants to automate test cases, write Playwright/Selenium scripts, or set up test automation.
---

# Test Automation Helper

Convert manual test cases into reliable automated tests.

## Defaults

- **UI web tests:** Playwright with TypeScript (or Python if the user prefers / the repo already uses Python).
- **API tests:** pytest + requests (Python) or Playwright APIRequestContext if the project is TS.
- **Mobile tests:** Maestro (simple YAML flows) for a quick start, Appium for a full framework — see the mobile-test skill for details.
- If the repo already has a framework (check for `playwright.config`, `pytest.ini`, `pom.xml`, `package.json`), follow the existing framework, structure, and naming instead of introducing a new one.

## Rules for good tests

- Use the Page Object Model for UI tests once there are more than a couple of tests.
- Selectors: prefer `getByRole`/`getByTestId`; never brittle XPath with indexes.
- No `sleep`/fixed waits — use auto-waiting or explicit waits on conditions.
- Each test independent: sets up its own data, no dependency on execution order.
- Assert on outcomes users care about (visible text, status codes, DB state), not implementation details.
- Add a clear test name that describes the scenario: `test("login fails with expired password shows reset link")`.

## Workflow

1. Read the manual test case(s) the user provides.
2. If no framework exists yet, scaffold a minimal one (config + one example test + README explaining how to run it) and confirm the structure with the user.
3. Write the automated tests.
4. **Run them** and show the results. If a test fails because the app is not reachable, say so clearly instead of "fixing" the test to pass.
5. Never weaken an assertion just to make a test green.
