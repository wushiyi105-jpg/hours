"""命令行：seed / log / report / bill / jobs / doctor / serve。"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import typer
from rich.console import Console

from ..adapters.export import bill_csv
from ..adapters.llm import build_llm
from ..adapters.notify import WebhookNotifier
from ..adapters.store import SqliteStore
from ..app.jobs import enqueue_weekly, run_due
from ..app.run import PROMPT, book, compose, report, week_range
from ..config import Settings
from ..config import settings as default_settings
from ..doctor import main as doctor_main

app = typer.Typer(help="工时台账：一句话记一笔", no_args_is_help=True)
console = Console()


def _settings(db: Path | None, port: int | None = None) -> Settings:
    s = default_settings.model_copy(deep=True)
    if db:
        s.db_path = db
    if port:
        s.port = port
    return s


def _store(settings: Settings) -> SqliteStore:
    return SqliteStore(settings.db_path)


@app.command()
def seed(db: Path = typer.Option(None)) -> None:
    """写入 3 个项目、双预算与一周工时。"""
    s = _settings(db)
    store = _store(s)
    data = json.loads(
        (Path(__file__).resolve().parents[2] / "data" / "seed.json").read_text(encoding="utf-8")
    )
    ids: dict[str, int] = {}
    for p in data["projects"]:
        ids[p["name"]] = store.add_project(p["name"], p["client"], p["rate"])
    for b in data["budgets"]:
        store.add_budget(ids[b["project"]], b["kind"], b["limit"])
    for e in data["entries"]:
        store.add_entry(ids[e["project"]], date.fromisoformat(e["day"]), e["start"], e["minutes"],
                        e["note"], e.get("confidence", 0.9))
    console.print(f"已写入 {len(data['projects'])} 个项目、{len(data['entries'])} 条工时")


@app.command()
def log(
    text: str = typer.Option(..., help="一句话，如「今天上午都在青禾改登录 3 小时」"),
    day: str = typer.Option("", help="YYYY-MM-DD"),
    start: int = typer.Option(540, help="开始时间，当天第几分钟"),
    db: Path = typer.Option(None),
) -> None:
    """口语入账。"""
    s = _settings(db)
    d = date.fromisoformat(day) if day else date.today()
    try:
        llm = build_llm(s.llm_base_url, s.llm_api_key, s.llm_model, PROMPT) if s.llm_enabled else None
        entry_id, data = book(_store(s), s, text, d, start, llm)
    except ValueError as exc:
        console.print(f"[red]{exc}[/]")
        raise typer.Exit(code=2) from exc
    console.print(f"已入账 #{entry_id}：{data['project']} {data['minutes']} 分钟")


@app.command("report")
def report_cmd(week: str = typer.Option("", help="2026-W48，默认本周"), db: Path = typer.Option(None)) -> None:
    """看周报与扣分。"""
    s = _settings(db)
    w = week or date.today().strftime("%G-W%V")
    try:
        result = report(_store(s), w)
    except ValueError as exc:
        console.print(f"[red]{exc}[/]")
        raise typer.Exit(code=2) from exc
    console.print(compose(_store(s), w))
    for f in result.report.findings:
        console.print(f"  [yellow]{f.rule_id}[/] -{f.penalty} {f.message}")
    console.print(f"合计扣分 {result.report.penalty_total}")




@app.command()
def bill(week: str = typer.Option(""), db: Path = typer.Option(None)) -> None:
    """出账单 CSV。"""
    s = _settings(db)
    w = week or date.today().strftime("%G-W%V")
    start, end = week_range(w)
    console.print(bill_csv(_store(s), start, end), end="")


@app.command()
def jobs(
    week: str = typer.Option(""), run: bool = typer.Option(False, "--run"), db: Path = typer.Option(None)
) -> None:
    """每周汇总提醒。"""
    s = _settings(db)
    store = _store(s)
    if run:
        console.print(f"发出 {run_due(store, s, date.today(), WebhookNotifier(s.webhook_url))} 条")
        return
    w = week or date.today().strftime("%G-W%V")
    console.print("已入队" if enqueue_weekly(store, w, date.today()) else "这周已排过")


@app.command()
def doctor(db: Path = typer.Option(None)) -> None:
    """四项体检。"""
    raise typer.Exit(code=doctor_main(_settings(db)))


@app.command()
def serve(port: int = typer.Option(None), db: Path = typer.Option(None)) -> None:
    """Web 界面。"""
    import uvicorn

    from .web import create_app

    s = _settings(db, port)
    uvicorn.run(create_app(s), host="127.0.0.1", port=s.port)


if __name__ == "__main__":
    main = app
    app()
