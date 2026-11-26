"""同一天同一项目，时间段相交就要报。"""

from __future__ import annotations

from ..models import Entry, Finding

PENALTY = 6


def overlaps(entries: list[Entry]) -> list[Finding]:
    out: list[Finding] = []
    ordered = sorted(entries, key=lambda e: (e.day, e.project_id, e.start))
    for prev, cur in zip(ordered, ordered[1:]):
        if prev.day != cur.day or prev.project_id != cur.project_id:
            continue
        if cur.start < prev.end:
            minutes = min(prev.end, cur.end) - cur.start
            out.append(
                Finding(
                    "overlap.entries",
                    f"{cur.day} 项目 {cur.project_id} 两条记录重叠 {minutes} 分钟",
                    PENALTY,
                    f"{prev.id}-{cur.id}",
                )
            )
    return out
