"""月底账单：3 个项目、4 档费率、4 种税率，一条命令出 CSV + 邮件正文。"""

from __future__ import annotations

from datetime import date

from ..domain.models import Project
from ..ports import StorePort

TAX_DEFAULT = 0.06


def month_range(month: str) -> tuple[date, date]:
    if len(month) != 7 or month[4] != "-":
        raise ValueError("month 形如 2026-11")
    year, mon = int(month[:4]), int(month[5:7])
    start = date(year, mon, 1)
    end = date(year + (mon == 12), (mon % 12) + 1, 1)
    return start, end


def aggregate(store: StorePort, projects: list[Project], month: str) -> list[dict]:
    start, end = month_range(month)
    entries = store.list_entries(start, end)
    by_project = {p.id: p for p in projects}
    rows: dict[int, dict] = {}
    for entry in entries:
        project = by_project.get(entry.project_id)
        if project is None:
            continue
        row = rows.setdefault(
            project.id,
            {"project": project.name, "client": project.client, "minutes": 0, "rate": project.rate},
        )
        row["minutes"] += entry.minutes
    for row in rows.values():
        row["hours"] = row["minutes"] / 60
        row["amount"] = round(row["hours"] * row["rate"], 2)
    return sorted(rows.values(), key=lambda r: r["amount"], reverse=True)


def csv_text(rows: list[dict], tax_rate: float, month: str) -> str:
    lines = ["项目,客户,工时,费率,金额,税率,税额,含税合计"]
    total = sum(r["amount"] for r in rows)
    tax = round(total * tax_rate, 2)
    for r in rows:
        line_tax = round(r["amount"] * tax_rate, 2)
        lines.append(
            f"{r['project']},{r['client']},{r['hours']:.2f},{r['rate']:.2f},"
            f"{r['amount']:.2f},{tax_rate:.0%},{line_tax:.2f},{r['amount'] + line_tax:.2f}"
        )
    lines.append(f"合计,,, ,{total:.2f},{tax_rate:.0%},{tax:.2f},{total + tax:.2f}")
    return "\n".join(lines) + "\n"


def email_text(rows: list[dict], tax_rate: float, month: str) -> str:
    total = sum(r["amount"] for r in rows)
    tax = round(total * tax_rate, 2)
    label = f"{month[:4]} 年 {int(month[5:7])} 月"
    lines = [
        f"# {label} 工时账单",
        "",
        f"主题：{label}技术服务费账单（含税 {total + tax:,.2f} 元）",
        "",
        "您好：",
        "",
        f"附件是 {label}的工时与费用明细，合计不含税 {total:,.2f} 元，税额 {tax:,.2f} 元，"
        f"含税 {total + tax:,.2f} 元。请核对，如有异议请在 3 个工作日内回复。",
        "",
        "| 项目 | 客户 | 工时 | 费率 | 金额 |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for r in rows:
        lines.append(
            f"| {r['project']} | {r['client']} | {r['hours']:.2f} h | {r['rate']:,.2f} | {r['amount']:,.2f} |"
        )
    lines += [
        f"| **合计** |  | **{sum(r['hours'] for r in rows):.2f} h** |  | **{total:,.2f}** |",
        "",
        f"税率：{tax_rate:.0%}；发票类型与税率以合同约定为准。",
        "",
        "顺颂商祺",
        "",
    ]
    return "\n".join(lines)
