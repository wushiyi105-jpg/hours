"""周核算：按项目汇总工时与金额，跑规则。"""

from __future__ import annotations

from dataclasses import dataclass

from .models import Budget, Entry, Finding, Project, Report
from .rules.budget import check as budget_check
from .rules.dayload import long_days
from .rules.overlap import overlaps
from .rules.rate import missing as rate_missing


@dataclass
class WeekResult:
    report: Report
    hours: dict[int, float]
    amount: dict[int, float]


def build(
    entries: list[Entry],
    projects: list[Project],
    budgets: list[Budget],
    week: str,
    count_rate_missing: bool = False,
) -> WeekResult:
    by_project = {p.id: p for p in projects}
    hours: dict[int, float] = {}
    amount: dict[int, float] = {}
    rows: list[tuple[str, str, float, float]] = []
    findings: list[Finding] = []
    for e in entries:
        p = by_project.get(e.project_id)
        name = p.name if p else f"#{e.project_id}"
        h = e.minutes / 60
        hours[e.project_id] = hours.get(e.project_id, 0.0) + h
        money = h * (p.rate if p else 0.0)
        amount[e.project_id] = amount.get(e.project_id, 0.0) + money
        rows.append((e.day.isoformat(), name, round(h, 2), round(money, 2)))
    findings += overlaps(entries)
    findings += long_days(entries)
    findings += budget_check(budgets, hours, amount)
    if count_rate_missing:
        findings += rate_missing(projects)
    total_minutes = sum(e.minutes for e in entries)
    report = Report(
        week=week,
        rows=rows,
        minutes=total_minutes,
        amount=round(sum(amount.values()), 2),
        findings=findings,
    )
    return WeekResult(report, hours, amount)
