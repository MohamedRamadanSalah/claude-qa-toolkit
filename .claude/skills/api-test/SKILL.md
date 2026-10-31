---
name: api-test
description: Test REST APIs — define test suites as JSON and run them with a bundled Python runner that validates status codes, response bodies, timing, and leaked stack traces. Use when the user wants to test an API, check endpoints, or verify API responses.
---

# API Tester

A bundled Python runner executes API tests deterministically. Your job is to WRITE the suite file well; the script does the running and checking. Follow this workflow.

## Workflow (mandatory)

1. **Gather**: base URL, auth (token/credentials), and either specific endpoints or a Swagger/OpenAPI spec (read it if given).
2. **Write the suite** to `api-tests/<name>.json`:

```json
{
  "base_url": "https://qa.example.com",
  "default_headers": {"Authorization": "Bearer <token>"},
  "tests": [
    {
      "name": "get user 1 - ok",
      "method": "GET",
      "path": "/api/users/1",
      "expect": {"status": 200, "max_time_s": 3, "json_fields": ["id", "email"], "json_equals": {"id": 1}}
    },
    {
      "name": "get user - no token - unauthorized",
      "method": "GET",
      "path": "/api/users/1",
      "headers": {"Authorization": ""},
      "expect": {"status": 401}
    }
  ]
}
```

   For EVERY endpoint, generate this standard set (skip only what doesn't apply):
   - valid request → 200/201 + expected fields (`json_fields`)
   - missing/invalid required fields → 400
   - no auth token → 401; wrong role → 403
   - non-existent ID → 404
   - boundary values in body (0, -1, max length, unicode)

3. **Run it:**

```
python .claude/skills/api-test/scripts/run_api_tests.py --suite api-tests/<name>.json --report api-tests/results.md
```

   - The script REFUSES to run if base_url doesn't look like a test environment (no dev/qa/test/staging/localhost in it). If blocked, ASK THE USER to confirm the environment before adding `--allow-any-env`. Never add that flag on your own.
   - The script also flags leaked stack traces in responses automatically — report those as security-relevant bugs.

4. **Report**: show the pass/fail table. For each failure, state expected vs actual in one line. Offer to write bug reports (bug-report skill) for real defects.

## Safety rules

- Never print full tokens — mask like `eyJhb...****` (the script masks automatically; you do the same in chat).
- No destructive requests (DELETE, bulk updates) without the user confirming the environment and approving explicitly.
