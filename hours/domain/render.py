"""离线周报文字。"""

from __future__ import annotations

from .models import Report


def render(report: Report) -> str:
    lines = [f"# 工时周报 {report.week}", ""]
    lines.append(f"合计 {report.minutes} 分钟，金额 {report.amount:.2f} 元")
    lines.append("")
    for day, name, h, money in report.rows:
        lines.append(f"- {day} {name} {h:g}h {money:.2f} 元")
    if report.findings:
        lines += ["", "## 需要看"]
        lines += [f"- {f.rule_id} -{f.penalty} {f.message}" for f in report.findings]
    return "\n".join(lines).rstrip() + "\n"
