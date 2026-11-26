"""甲方账单 CSV：与周报同一口径。"""

from __future__ import annotations

from ..store.sqlite import SqliteStore


def bill_csv(store: SqliteStore, start, end) -> str:
    projects = {p.id: p for p in store.list_projects()}
    rows = ["date,project,client,hours,rate,amount"]
    total = 0.0
    for e in store.list_entries(start, end):
        p = projects.get(e.project_id)
        name = p.name if p else f"#{e.project_id}"
        client = p.client if p else ""
        h = e.minutes / 60
        money = h * (p.rate if p else 0.0)
        total += money
        rows.append(f"{e.day},{name},{client},{h:.2f},{p.rate if p else 0:.2f},{money:.2f}")
    rows.append(f"total,,,,,{total:.2f}")
    return "\n".join(rows) + "\n"
