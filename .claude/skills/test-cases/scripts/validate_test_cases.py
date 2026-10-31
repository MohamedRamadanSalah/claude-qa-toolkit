#!/usr/bin/env python3
"""Test case table linter. Parses the markdown test-case table and checks
IDs, required fields, priorities, and coverage of categories.
The AI MUST run this on every test-case file it writes and fix all ERRORs.

Usage: python validate_test_cases.py <test-cases.md>
Exit code 0 = clean, 1 = has errors.

Expected table columns (exact order):
| ID | Category | Title | Preconditions | Steps | Test Data | Expected Result | Priority |
"""
import re
import sys
from pathlib import Path

COLUMNS = ["ID", "Category", "Title", "Preconditions", "Steps", "Test Data", "Expected Result", "Priority"]
VALID_CATEGORIES = ["Positive", "Negative", "Boundary", "Edge", "Non-functional"]
VALID_PRIORITIES = ["P1", "P2", "P3"]
REQUIRED_COVERAGE = ["Positive", "Negative", "Boundary"]
PLACEHOLDERS = {"", "...", "-", "n/a", "tbd", "todo"}


def parse_table(md):
    rows = []
    for line in md.splitlines():
        line = line.strip()
        if not line.startswith("|") or re.match(r"^\|[\s\-:|]+\|$", line):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        rows.append(cells)
    return rows


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    md = Path(sys.argv[1]).read_text(encoding="utf-8-sig")
    rows = parse_table(md)
    errors, warnings = [], []

    if not rows:
        print("ERROR: no markdown table found in the file")
        return 1

    header = rows[0]
    if [h.lower() for h in header] != [c.lower() for c in COLUMNS]:
        errors.append(f"table header must be exactly: | {' | '.join(COLUMNS)} |  (got: | {' | '.join(header)} |)")
        print(f"ERROR: {errors[0]}")
        return 1

    cases = rows[1:]
    if len(cases) < 5:
        warnings.append(f"only {len(cases)} test cases — a real feature usually needs more")

    seen_ids, categories = set(), []
    for n, c in enumerate(cases, 2):  # row number in table for messages
        if len(c) != len(COLUMNS):
            errors.append(f"row {n}: has {len(c)} cells, expected {len(COLUMNS)}")
            continue
        tc_id, cat, title, precond, steps, data, expected, prio = c

        if not re.match(r"^TC-\d{3,}$", tc_id):
            errors.append(f"row {n}: ID '{tc_id}' must match TC-001 pattern")
        if tc_id in seen_ids:
            errors.append(f"row {n}: duplicate ID {tc_id}")
        seen_ids.add(tc_id)

        if cat not in VALID_CATEGORIES:
            errors.append(f"{tc_id}: category '{cat}' invalid — use {'/'.join(VALID_CATEGORIES)}")
        categories.append(cat)

        for field, value, min_len in (("Title", title, 15), ("Steps", steps, 20), ("Expected Result", expected, 10)):
            if value.lower() in PLACEHOLDERS:
                errors.append(f"{tc_id}: {field} is empty/placeholder")
            elif len(value) < min_len:
                errors.append(f"{tc_id}: {field} too short ('{value}') — must be concrete")

        if steps.lower() not in PLACEHOLDERS and not re.search(r"\d[.)]", steps):
            warnings.append(f"{tc_id}: Steps have no numbering — write '1. ... 2. ...' (use <br> for line breaks in the cell)")
        if expected.strip().lower() in ("works", "it works", "success", "ok", "no error", "as expected"):
            errors.append(f"{tc_id}: Expected Result '{expected}' is vague — state the exact observable outcome")
        if prio not in VALID_PRIORITIES:
            errors.append(f"{tc_id}: priority '{prio}' invalid — use P1/P2/P3")

    for req in REQUIRED_COVERAGE:
        if req not in categories:
            errors.append(f"COVERAGE GAP: no '{req}' test case — every feature needs at least one")
    if "Edge" not in categories:
        warnings.append("no 'Edge' category cases (interruption, concurrency, unicode...) — usually worth adding")

    counts = {c: categories.count(c) for c in VALID_CATEGORIES if categories.count(c)}
    print(f"Parsed {len(cases)} test cases. Coverage: " + ", ".join(f"{k}={v}" for k, v in counts.items()))
    for e in errors:
        print(f"ERROR: {e}")
    for w in warnings:
        print(f"WARN:  {w}")
    if not errors:
        print("OK: test cases pass all checks" + (f" ({len(warnings)} warnings)" if warnings else ""))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
