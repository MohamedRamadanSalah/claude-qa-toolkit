#!/usr/bin/env python3
"""Deterministic test data generator (stdlib only).

Usage:
  python generate_data.py --type users --count 50 --format csv --out test-data/users.csv
  python generate_data.py --type products --count 100 --format json --out test-data/products.json
  python generate_data.py --type orders --count 20 --format sql --table orders --out test-data/orders.sql
  Add --no-edge-cases to skip the edge-case rows. Add --seed 42 for reproducible data.
"""
import argparse
import csv
import io
import json
import random
import sys
from pathlib import Path

FIRST_NAMES = ["Mohamed", "Ahmed", "Sara", "Fatma", "Omar", "Layla", "John", "Maria",
               "Wei", "Yuki", "Ivan", "Anna", "Carlos", "Priya", "Amir", "Nour"]
LAST_NAMES = ["Ramadan", "Hassan", "Ali", "Smith", "Garcia", "Chen", "Tanaka",
              "Petrov", "Khan", "Mostafa", "Ibrahim", "Johnson", "Silva", "Saleh"]
CITIES = ["Cairo", "Alexandria", "Giza", "Dubai", "Riyadh", "London", "Berlin", "Tokyo"]
PRODUCT_ADJ = ["Smart", "Classic", "Pro", "Mini", "Ultra", "Eco", "Premium", "Basic"]
PRODUCT_NOUN = ["Phone", "Laptop", "Headset", "Charger", "Keyboard", "Monitor", "Camera", "Router"]
ORDER_STATUSES = ["pending", "paid", "shipped", "delivered", "cancelled", "refunded"]

# Edge-case string values every input field should survive
EDGE_STRINGS = [
    ("empty string", ""),
    ("single char", "a"),
    ("255 chars (common max)", "x" * 255),
    ("256 chars (max+1)", "x" * 256),
    ("leading/trailing spaces", "  spaced  "),
    ("unicode + emoji", "Ωmega 文字 🚀"),
    ("arabic RTL", "مرحبا بالعالم"),
    ("sql injection probe", "' OR 1=1 --"),
    ("html/xss probe", "<script>alert(1)</script>"),
    ("only whitespace", "   "),
]


def make_user(i, rng):
    first = rng.choice(FIRST_NAMES)
    last = rng.choice(LAST_NAMES)
    return {
        "id": i,
        "first_name": first,
        "last_name": last,
        "email": f"{first.lower()}.{last.lower()}{i}@example.com",
        "phone": f"+1555{rng.randint(1000000, 9999999)}",  # 555 = reserved fake range
        "city": rng.choice(CITIES),
        "age": rng.randint(18, 80),
        "active": rng.choice([True, False]),
        "created_at": f"2025-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
        "_note": "",
    }


def make_product(i, rng):
    return {
        "id": i,
        "name": f"{rng.choice(PRODUCT_ADJ)} {rng.choice(PRODUCT_NOUN)} {i}",
        "sku": f"SKU-{i:06d}",
        "price": round(rng.uniform(1, 2000), 2),
        "stock": rng.randint(0, 500),
        "category": rng.choice(PRODUCT_NOUN),
        "active": rng.choice([True, False]),
        "_note": "",
    }


def make_order(i, rng):
    qty = rng.randint(1, 10)
    unit = round(rng.uniform(1, 500), 2)
    return {
        "id": i,
        "order_number": f"ORD-2025-{i:06d}",
        "user_id": rng.randint(1, 1000),
        "quantity": qty,
        "unit_price": unit,
        "total": round(qty * unit, 2),
        "status": rng.choice(ORDER_STATUSES),
        "order_date": f"2025-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
        "_note": "",
    }


MAKERS = {"users": make_user, "products": make_product, "orders": make_order}


def edge_rows(entity, start_id):
    """Deterministic edge-case rows: boundary numbers, tricky strings, odd dates."""
    rows = []
    i = start_id
    base = MAKERS[entity](0, random.Random(0))
    text_field = {"users": "first_name", "products": "name", "orders": "order_number"}[entity]
    num_field = {"users": "age", "products": "price", "orders": "total"}[entity]

    for note, value in EDGE_STRINGS:
        r = MAKERS[entity](i, random.Random(i))
        r[text_field] = value
        r["_note"] = f"edge: {note}"
        rows.append(r)
        i += 1

    for note, value in [("zero", 0), ("negative", -1), ("huge number", 999999999),
                        ("decimal where int expected", 3.14)]:
        r = MAKERS[entity](i, random.Random(i))
        r[num_field] = value
        r["_note"] = f"edge: {note}"
        rows.append(r)
        i += 1

    if "created_at" in base or "order_date" in base:
        date_field = "created_at" if "created_at" in base else "order_date"
        for note, value in [("leap day", "2024-02-29"), ("end of year", "2025-12-31"),
                            ("far future", "2099-01-01"), ("far past", "1900-01-01"),
                            ("invalid date", "2025-02-30")]:
            r = MAKERS[entity](i, random.Random(i))
            r[date_field] = value
            r["_note"] = f"edge: {note}"
            rows.append(r)
            i += 1
    return rows


def sql_escape(v):
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, (int, float)):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--type", required=True, choices=sorted(MAKERS))
    p.add_argument("--count", type=int, default=20)
    p.add_argument("--format", default="csv", choices=["csv", "json", "sql"])
    p.add_argument("--out", required=True)
    p.add_argument("--table", default=None, help="table name for sql format")
    p.add_argument("--seed", type=int, default=1234)
    p.add_argument("--no-edge-cases", action="store_true")
    a = p.parse_args()

    rng = random.Random(a.seed)
    rows = [MAKERS[a.type](i + 1, rng) for i in range(a.count)]
    n_edge = 0
    if not a.no_edge_cases:
        extra = edge_rows(a.type, a.count + 1)
        rows += extra
        n_edge = len(extra)

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    if a.format == "json":
        out.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    elif a.format == "csv":
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
        out.write_text(buf.getvalue(), encoding="utf-8-sig")  # BOM so Excel opens Arabic correctly
    else:
        table = a.table or a.type
        lines = []
        for r in rows:
            cols = ", ".join(k for k in r if k != "_note")
            vals = ", ".join(sql_escape(v) for k, v in r.items() if k != "_note")
            note = f"  -- {r['_note']}" if r["_note"] else ""
            lines.append(f"INSERT INTO {table} ({cols}) VALUES ({vals});{note}")
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"OK: wrote {len(rows)} rows ({a.count} normal + {n_edge} edge-case) to {out}")


if __name__ == "__main__":
    sys.exit(main())
