"""用例：口语 → 本地拆条 → 模型补描述 → 入账；周报与账单。"""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from ..config import Settings
from ..domain.engine import WeekResult, build
from ..domain.models import Project
from ..domain.render import render
from ..domain.rules.parse import parse
from ..ports import LLMPort, StorePort

PROMPT = (Path(__file__).resolve().parents[2] / "prompts" / "parse.md").read_text(encoding="utf-8")


def week_range(week: str) -> tuple[date, date]:
    if len(week) < 8 or "-W" not in week:
        raise ValueError("week 形如 2026-W48")
    year, num = week.split("-W")
    start = date.fromisocalendar(int(year), int(num), 1)
    return start, start + timedelta(days=6)


def parse_text(
    text: str, projects: list[Project], settings: Settings, llm: LLMPort | None = None
) -> dict[str, Any]:
    names = [p.name for p in projects]
    project, minutes, conf = parse(text, names)
    out: dict[str, Any] = {"project": project, "minutes": minutes, "note": text.strip(), "confidence": conf}
    if llm is not None:
        try:
            raw = llm.write(PROMPT, f"projects={names}\ntext={text}")
            data = json.loads(raw.strip().strip("`").removeprefix("json"))
            if isinstance(data, dict):
                out.update({k: data.get(k, out[k]) for k in ("project", "minutes", "note", "confidence")})
        except Exception:  # noqa: BLE001 模型胡了就退回本地拆条
            pass
    out["minutes"] = int(out["minutes"])
    out["confidence"] = float(out["confidence"])
    out["project"] = str(out["project"])
    if out["confidence"] < 0.6:
        raise ValueError(f"置信度太低（{out['confidence']:.2f}），只作建议不入账")
    if out["minutes"] <= 0 or out["minutes"] > 1440:
        raise ValueError("拆不出有效时长（1-1440 分钟）")
    if out["project"] not in names:
        raise ValueError(f"项目不在清单里：{out['project'] or '未识别'}")
    return out


Booking = tuple[int, dict]


def book(
    store: StorePort, settings: Settings, text: str, day: date, start: int, llm: LLMPort | None = None
) -> Booking:
    projects = store.list_projects()
    data = parse_text(text, projects, settings, llm)
    if data["confidence"] < 0.6:
        raise ValueError(f"置信度太低（{data['confidence']:.2f}），只作建议不入账")
    by_name = {p.name: p for p in projects}
    pid = by_name[data["project"]].id
    entry_id = store.add_entry(pid, day, start, data["minutes"], data["note"], data["confidence"])
    return entry_id, data


def report(store: StorePort, week: str) -> WeekResult:
    start, end = week_range(week)
    return build(
        store.list_entries(start, end), store.list_projects(), store.list_budgets(), week,
        count_rate_missing=True,
    )


def compose(store: StorePort, week: str) -> str:
    return render(report(store, week).report)


