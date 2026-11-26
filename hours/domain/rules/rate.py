"""费率：没费率不能出账单，也不能假装有金额。"""

from __future__ import annotations

from ..models import Finding, Project

PENALTY = 10


def missing(projects: list[Project]) -> list[Finding]:
    return [
        Finding("rate.missing", f"{p.name} 没填费率，账单金额算不出来", PENALTY, p.name)
        for p in projects
        if p.rate <= 0
    ]
