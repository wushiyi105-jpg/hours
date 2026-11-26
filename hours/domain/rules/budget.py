"""双预算：工时与金额各一条线，80% 预警，100% 超支。"""

from __future__ import annotations

from ..models import Budget, Finding

WARN = 0.8
WARN_PENALTY = 3
OVER_PENALTY = 10


def check(
    budgets: list[Budget], hours: dict[int, float], amount: dict[int, float]
) -> list[Finding]:
    out: list[Finding] = []
    for b in budgets:
        used = hours.get(b.project_id, 0.0) if b.kind == "hours" else amount.get(b.project_id, 0.0)
        if b.limit <= 0:
            continue
        ratio = used / b.limit
        if ratio >= 1.0:
            out.append(
                Finding(
                    "budget.over",
                    f"项目 {b.project_id} {b.kind} 已用 {ratio:.0%}（{used:g}/{b.limit:g}）",
                    OVER_PENALTY,
                    f"{b.project_id}:{b.kind}",
                )
            )
        elif ratio >= WARN:
            out.append(
                Finding(
                    "budget.warn",
                    f"项目 {b.project_id} {b.kind} 到 {ratio:.0%}，过 80% 了",
                    WARN_PENALTY,
                    f"{b.project_id}:{b.kind}",
                )
            )
    return out
