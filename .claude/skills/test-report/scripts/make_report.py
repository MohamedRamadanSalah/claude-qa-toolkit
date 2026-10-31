#!/usr/bin/env python3
"""Test summary report generator (stdlib only). All math and the go/no-go
verdict are computed HERE deterministically — never by the AI.

Usage:
  python make_report.py --in results.json [--out report.md]

Input JSON shape:
{
  "project": "MyApp v2.3",
  "date": "2026-07-07",
  "total": 120, "passed": 100, "failed": 12, "blocked": 3,   # not_run is computed
  "defects": [
    {"id": "BUG-1", "severity": "Critical", "status": "Open",  "title": "Login crash"},
    {"id": "BUG-2", "severity": "Minor",    "status": "Fixed", "title": "Typo"}
  ],
  "notes": "optional free text"
}
Severity must be one of: Blocker, Critical, Major, Minor, Trivial.
Status must be one of: Open, Fixed, Deferred.
"""
import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows console can't print emoji in cp1252

SEVERITIES = ["Blocker", "Critical", "Major", "Minor", "Trivial"]
STATUSES = ["Open", "Fixed", "Deferred"]


def pct(part, whole):
    return f"{(100.0 * part / whole):.1f}%" if whole else "n/a"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="inp", required=True)
    p.add_argument("--out", default=None)
    a = p.parse_args()

    data = json.loads(Path(a.inp).read_text(encoding="utf-8-sig"))

    errors = []
    total = int(data.get("total", 0))
    passed = int(data.get("passed", 0))
    failed = int(data.get("failed", 0))
    blocked = int(data.get("blocked", 0))
    executed = passed + failed + blocked
    not_run = total - executed

    if total <= 0:
        errors.append("total must be > 0")
    if not_run < 0:
        errors.append(f"passed+failed+blocked ({executed}) is greater than total ({total}) — numbers are inconsistent")

    defects = data.get("defects", [])
    for d in defects:
        if d.get("severity") not in SEVERITIES:
            errors.append(f"defect {d.get('id')}: severity '{d.get('severity')}' invalid (use {'/'.join(SEVERITIES)})")
        if d.get("status") not in STATUSES:
            errors.append(f"defect {d.get('id')}: status '{d.get('status')}' invalid (use {'/'.join(STATUSES)})")

    if errors:
        print("INPUT ERRORS — fix results.json and run again:")
        for e in errors:
            print(f"  - {e}")
        return 1

    open_by_sev = {s: [d for d in defects if d["status"] == "Open" and d["severity"] == s] for s in SEVERITIES}
    n_open_crit = len(open_by_sev["Blocker"]) + len(open_by_sev["Critical"])
    n_open_major = len(open_by_sev["Major"])
    fail_rate = failed / executed if executed else 0
    exec_rate = executed / total

    # Deterministic verdict rules (in priority order)
    reasons = []
    if n_open_crit > 0:
        verdict = "❌ NOT READY"
        reasons.append(f"{n_open_crit} open Blocker/Critical defect(s)")
    elif exec_rate < 0.90:
        verdict = "❌ NOT READY"
        reasons.append(f"only {pct(executed, total)} of test cases executed (need ≥ 90%)")
    elif blocked > total * 0.10:
        verdict = "❌ NOT READY"
        reasons.append(f"{blocked} blocked cases ({pct(blocked, total)}) — testing could not finish")
    elif fail_rate > 0.10 or n_open_major > 0:
        verdict = "⚠️ RELEASE WITH RISK"
        if fail_rate > 0.10:
            reasons.append(f"failure rate {pct(failed, executed)} (above 10%)")
        if n_open_major > 0:
            reasons.append(f"{n_open_major} open Major defect(s)")
    else:
        verdict = "✅ READY TO RELEASE"
        reasons.append("execution ≥ 90%, no open Blocker/Critical/Major defects, failure rate ≤ 10%")

    L = []
    L.append(f"# Test Summary Report — {data.get('project', 'Project')}")
    L.append(f"\n**Date:** {data.get('date', '')}  ")
    L.append(f"**Verdict: {verdict}** — {'; '.join(reasons)}\n")
    L.append("## Execution status\n")
    L.append("| Metric | Count | % of total |")
    L.append("|---|---:|---:|")
    L.append(f"| Total test cases | {total} | 100% |")
    L.append(f"| Executed | {executed} | {pct(executed, total)} |")
    L.append(f"| Passed | {passed} | {pct(passed, total)} |")
    L.append(f"| Failed | {failed} | {pct(failed, total)} |")
    L.append(f"| Blocked | {blocked} | {pct(blocked, total)} |")
    L.append(f"| Not run | {not_run} | {pct(not_run, total)} |")
    L.append(f"\nPass rate of executed cases: **{pct(passed, executed)}**\n")

    L.append("## Defects\n")
    if defects:
        L.append("| Severity | Open | Fixed | Deferred |")
        L.append("|---|---:|---:|---:|")
        for s in SEVERITIES:
            row = [d for d in defects if d["severity"] == s]
            if row:
                L.append(f"| {s} | {sum(d['status'] == 'Open' for d in row)} "
                         f"| {sum(d['status'] == 'Fixed' for d in row)} "
                         f"| {sum(d['status'] == 'Deferred' for d in row)} |")
        opens = [d for d in defects if d["status"] == "Open" and d["severity"] in ("Blocker", "Critical", "Major")]
        if opens:
            L.append("\n**Open high-severity defects:**")
            for d in opens:
                L.append(f"- **{d['id']}** ({d['severity']}): {d.get('title', '')}")
    else:
        L.append("No defects reported.")

    if data.get("notes"):
        L.append(f"\n## Notes\n\n{data['notes']}")

    report = "\n".join(L) + "\n"
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(report, encoding="utf-8")
        print(f"OK: report written to {a.out} — verdict: {verdict}")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
