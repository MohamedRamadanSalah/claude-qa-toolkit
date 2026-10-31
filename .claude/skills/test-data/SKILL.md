---
name: test-data
description: Generate realistic test data — users, products, orders as CSV/JSON/SQL files, including edge-case values (unicode, boundaries, injection strings). Use when the user needs test data, dummy data, or data files for testing.
---

# Test Data Generator

A ready-made Python generator does the accurate work. DO NOT hand-write rows of data — run the script.

## Workflow (mandatory)

1. Ask only what's not obvious: entity type, how many rows, and format (CSV / JSON / SQL).
2. Run the generator:

```
python .claude/skills/test-data/scripts/generate_data.py --type users --count 50 --format csv --out test-data/users.csv
```

   - `--type`: `users` | `products` | `orders`
   - `--format`: `csv` (Excel-friendly, UTF-8 BOM) | `json` | `sql` (add `--table <name>`)
   - `--seed <n>`: same seed → identical data every run (default 1234)
   - `--no-edge-cases`: plain data only

   By default the script APPENDS edge-case rows (marked in the `_note` column): empty/max-length strings, unicode + Arabic RTL text, SQL/XSS probe strings, zero/negative/huge numbers, leap day and invalid dates. Tell the user these rows exist and what they are for.

3. Show the user the script's output line (row counts + file path) and the first few rows of the file.

## If the user needs an entity the script doesn't have

(e.g. patients, invoices, bookings): copy the pattern in `generate_data.py` — add a `make_<entity>` function and register it in `MAKERS`, then run it. Keep it stdlib-only, keep the `_note` column, keep emails on `@example.com` and phones in the fake `555` range.

## Hard rules

- NEVER generate real personal data. For credit cards use official test numbers only (e.g. Stripe's 4242 4242 4242 4242).
- Output files always go in the `test-data/` folder.
- For a quick copy-paste list of nasty input strings (no file), just print the `EDGE_STRINGS` list from the script.
