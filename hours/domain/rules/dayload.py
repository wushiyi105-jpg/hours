"""单日上限：超过 16 小时多半记错了。"""

from __future__ import annotations

from ..models import Entry, Finding

LIMIT = 960
PENALTY = 8


def long_days(entries: list[Entry]) -> list[Finding]:
    totals: dict[str, int] = {}
    for e in entries:
        totals[e.day.isoformat()] = totals.get(e.day.isoformat(), 0) + e.minutes
    return [
        Finding("entry.long_day", f"{day} 记了 {minutes} 分钟，超过 16 小时", PENALTY, day)
        for day, minutes in totals.items()
        if minutes > LIMIT
    ]
