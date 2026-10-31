---
name: exploratory
description: Create exploratory testing charters and session ideas for a feature — where to look for bugs, what to try, tours and heuristics. Use when the user wants exploratory testing ideas, a testing tour, or "what should I test" guidance for a feature.
---

# Exploratory Testing Guide

Help the tester plan exploratory testing sessions for a feature they describe.

## Output

Produce 3-6 **charters**, each in this format:

> **Charter:** Explore <area> using <resources/approach> to discover <kind of problems>
> **Time box:** 30-60 min
> **Ideas to try:** 5-10 concrete, creative things to attempt

## Where to find good ideas

Apply heuristics relevant to the feature (pick what fits, don't dump all):
- **CRUD tour** — create, read, update, delete everything; delete things that are in use elsewhere
- **Interruption tour** — cancel mid-operation, refresh during save, kill network, go back button, double-click submit
- **Data tour** — extreme values, wrong formats, copy-paste with formatting, autofill
- **State tour** — expired session, second tab, concurrent edits by two users
- **Permission tour** — every role tries every action, including via direct URL/API
- **Environment tour** — small screen, slow network (throttle), different browser/locale/timezone
- **History tour** — upgrade with old data, previously-saved drafts, legacy records

End with a short **"Most likely bug hiding spots"** list — your top 3 guesses for where this specific feature will break, with reasoning.
