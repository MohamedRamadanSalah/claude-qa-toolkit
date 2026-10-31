#!/usr/bin/env python3
"""API test runner (stdlib only — no pip installs needed).
Executes a JSON-defined test suite and prints a pass/fail report.

Usage:
  python run_api_tests.py --suite tests.json [--report results.md] [--allow-any-env]

Suite JSON shape:
{
  "base_url": "https://qa.example.com",
  "default_headers": {"Authorization": "Bearer XXX", "Content-Type": "application/json"},
  "tests": [
    {
      "name": "get user by id - ok",
      "method": "GET",
      "path": "/api/users/1",
      "headers": {},                      # optional, merged over defaults
      "body": {"k": "v"},                 # optional, sent as JSON
      "expect": {
        "status": 200,                    # required
        "max_time_s": 3,                  # optional
        "body_contains": ["email"],       # optional substrings
        "json_fields": ["id", "email"],   # optional top-level fields that must exist
        "json_equals": {"id": 1}          # optional exact top-level values
      }
    }
  ]
}
"""
import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows console can't print emoji in cp1252

SAFE_ENV_MARKERS = ("localhost", "127.0.0.1", "0.0.0.0", "dev", "qa", "test", "stag", "sandbox", "mock", "demo")


def mask(value: str) -> str:
    return value[:10] + "****" if len(value) > 10 else "****"


def run_test(base_url, defaults, t):
    url = base_url.rstrip("/") + t["path"]
    headers = {**defaults, **t.get("headers", {})}
    body = None
    if t.get("body") is not None:
        body = json.dumps(t["body"]).encode("utf-8")
        headers.setdefault("Content-Type", "application/json")

    req = urllib.request.Request(url, data=body, method=t.get("method", "GET").upper())
    for k, v in headers.items():
        req.add_header(k, v)

    start = time.monotonic()
    body_read_failed = False
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            status = resp.status
            try:
                text = resp.read().decode("utf-8", "replace")
            except Exception:  # status already received; a stalled body must not void the test
                text, body_read_failed = "", True
    except urllib.error.HTTPError as e:
        status = e.code
        try:
            text = e.read().decode("utf-8", "replace")
        except Exception:
            text, body_read_failed = "", True
    except Exception as e:
        return {"name": t["name"], "pass": False, "status": None, "time": time.monotonic() - start,
                "problems": [f"request failed: {type(e).__name__}: {e}"], "body": ""}
    elapsed = time.monotonic() - start

    exp = t.get("expect", {})
    problems = []
    if "status" in exp and status != exp["status"]:
        problems.append(f"status: expected {exp['status']}, got {status}")
    if body_read_failed and (exp.get("body_contains") or exp.get("json_fields") or exp.get("json_equals")):
        problems.append("could not read response body (connection stalled) — body checks skipped, re-run to confirm")
    if "max_time_s" in exp and elapsed > exp["max_time_s"]:
        problems.append(f"too slow: {elapsed:.2f}s > {exp['max_time_s']}s")
    for sub in exp.get("body_contains", []):
        if sub not in text:
            problems.append(f"body missing substring: '{sub}'")
    if exp.get("json_fields") or exp.get("json_equals"):
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            problems.append("response is not valid JSON")
            data = None
        if isinstance(data, dict):
            for f in exp.get("json_fields", []):
                if f not in data:
                    problems.append(f"json field missing: '{f}'")
            for k, v in exp.get("json_equals", {}).items():
                if data.get(k) != v:
                    problems.append(f"json '{k}': expected {v!r}, got {data.get(k)!r}")

    # Generic smell checks even when the test passes
    if re.search(r"(Traceback \(most recent call last\)|at [\w.$]+\(\w+\.java:\d+\)|System\.\w+Exception)", text):
        problems.append("SMELL: stack trace leaked in response body")

    return {"name": t["name"], "pass": not problems, "status": status,
            "time": elapsed, "problems": problems, "body": text[:300]}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--suite", required=True)
    p.add_argument("--report", default=None)
    p.add_argument("--allow-any-env", action="store_true",
                   help="skip the production-URL safety check (use only with explicit user approval)")
    a = p.parse_args()

    suite = json.loads(Path(a.suite).read_text(encoding="utf-8-sig"))
    base_url = suite["base_url"]

    if not a.allow_any_env and not any(m in base_url.lower() for m in SAFE_ENV_MARKERS):
        print(f"BLOCKED: base_url '{base_url}' does not look like a test environment "
              f"(no dev/qa/test/staging/localhost in it). This might be PRODUCTION.")
        print("If the user confirms it is safe, re-run with --allow-any-env.")
        return 2

    results = [run_test(base_url, suite.get("default_headers", {}), t) for t in suite.get("tests", [])]
    n_pass = sum(r["pass"] for r in results)

    L = [f"# API Test Results — {base_url}", "",
         f"**{n_pass}/{len(results)} passed**", "",
         "| # | Test | Status | Time | Result |", "|---|---|---|---|---|"]
    for i, r in enumerate(results, 1):
        outcome = "✅ PASS" if r["pass"] else "❌ FAIL"
        L.append(f"| {i} | {r['name']} | {r['status']} | {r['time']:.2f}s | {outcome} |")
    fails = [r for r in results if not r["pass"]]
    if fails:
        L.append("\n## Failures\n")
        for r in fails:
            L.append(f"### {r['name']}")
            for prob in r["problems"]:
                L.append(f"- {prob}")
            if r["body"]:
                L.append(f"\nResponse (first 300 chars):\n```\n{r['body']}\n```")
    report = "\n".join(L) + "\n"

    print(report)
    if a.report:
        Path(a.report).parent.mkdir(parents=True, exist_ok=True)
        Path(a.report).write_text(report, encoding="utf-8")
        print(f"(saved to {a.report})")
    return 0 if n_pass == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
