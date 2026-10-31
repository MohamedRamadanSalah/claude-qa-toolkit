#!/usr/bin/env python3
"""Bug report linter. Checks a markdown bug report for completeness and quality.
The AI MUST run this on every bug report it writes and fix all ERRORs.

Usage: python validate_bug_report.py <report.md>
Exit code 0 = clean, 1 = has errors.
"""
import re
import sys
from pathlib import Path

REQUIRED_SECTIONS = ["Title", "Environment", "Severity", "Priority",
                     "Steps to Reproduce", "Actual Result", "Expected Result"]
VALID_SEVERITY = ["Blocker", "Critical", "Major", "Minor", "Trivial"]
VALID_PRIORITY = ["P1", "P2", "P3"]
VAGUE_TITLES = ["not working", "doesn't work", "does not work", "broken", "issue", "problem", "bug", "error occurs", "something wrong"]
VAGUE_RESULTS = ["it fails", "doesn't work", "error", "wrong", "not correct", "something happens"]


def section_text(md, name):
    """Text between **Name:** and the next **Header:** (or end)."""
    m = re.search(rf"\*\*{re.escape(name)}:?\*\*:?\s*(.*?)(?=\n\*\*[A-Z]|\Z)", md, re.S)
    return m.group(1).strip() if m else None


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    md = Path(sys.argv[1]).read_text(encoding="utf-8-sig")
    errors, warnings = [], []

    for s in REQUIRED_SECTIONS:
        body = section_text(md, s)
        if body is None:
            errors.append(f"missing section: **{s}:**")
        elif not body or body in ("...", "-", "N/A", "TBD"):
            errors.append(f"section **{s}** is empty or a placeholder")

    title = section_text(md, "Title") or ""
    if title:
        if len(title) < 25:
            errors.append(f"title too short ({len(title)} chars) — must describe component + what fails + condition")
        low = title.lower()
        for v in VAGUE_TITLES:
            if v in low and len(title) < 60:
                warnings.append(f"title contains vague phrase '{v}' — be specific about WHAT fails and WHEN")
                break
        if not title.startswith("["):
            warnings.append("title should start with a [Component] tag, e.g. [Login]")

    sev = section_text(md, "Severity") or ""
    if sev and not any(v in sev for v in VALID_SEVERITY):
        errors.append(f"severity '{sev}' invalid — use one of: {', '.join(VALID_SEVERITY)}")
    pri = section_text(md, "Priority") or ""
    if pri and not any(v in pri for v in VALID_PRIORITY):
        errors.append(f"priority '{pri}' invalid — use one of: {', '.join(VALID_PRIORITY)}")

    steps = section_text(md, "Steps to Reproduce") or ""
    numbered = re.findall(r"^\s*\d+\.", steps, re.M)
    if steps and len(numbered) < 2:
        errors.append(f"Steps to Reproduce has {len(numbered)} numbered step(s) — need at least 2, numbered like '1.'")

    actual = section_text(md, "Actual Result") or ""
    expected = section_text(md, "Expected Result") or ""
    if actual and expected and actual.strip().lower() == expected.strip().lower():
        errors.append("Actual Result and Expected Result are identical — that is not a bug description")
    for name, txt in (("Actual Result", actual), ("Expected Result", expected)):
        if txt and len(txt) < 15:
            errors.append(f"{name} too short ('{txt}') — describe it concretely")
        low = txt.lower()
        if any(low == v or low.startswith(v) for v in VAGUE_RESULTS):
            errors.append(f"{name} is vague ('{txt}') — include exact behavior/error text")

    env = section_text(md, "Environment") or ""
    if env and not re.search(r"\d", env):
        warnings.append("Environment has no version numbers — add OS/app/browser versions")

    if not re.search(r"\*\*Reproducibility:?\*\*", md):
        warnings.append("no Reproducibility section — add 'Always' or 'x out of y tries'")

    for e in errors:
        print(f"ERROR: {e}")
    for w in warnings:
        print(f"WARN:  {w}")
    if not errors and not warnings:
        print("OK: bug report passes all checks")
    elif not errors:
        print(f"OK with {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
