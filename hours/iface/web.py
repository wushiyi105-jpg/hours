"""FastAPI + Jinja2：一句话录入、周报、账单。"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ..adapters.export import bill_csv
from ..adapters.llm import build_llm
from ..adapters.store import SqliteStore
from ..app.run import PROMPT, book, compose, report, week_range
from ..config import Settings

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).resolve().parents[2] / "templates"))


def current_week() -> str:
    return date.today().strftime("%G-W%V")


def create_app(settings: Settings, store: SqliteStore | None = None) -> FastAPI:
    app = FastAPI(title="Hours", version="1.0.0")
    app.mount(
        "/static",
        StaticFiles(directory=str(Path(__file__).resolve().parents[2] / "static")),
        name="static",
    )
    store = store or SqliteStore(settings.db_path)
    llm = build_llm(settings.llm_base_url, settings.llm_api_key, settings.llm_model, PROMPT) if settings.llm_enabled else None

    def render(request: Request, week: str, error: str = "", message: str = "") -> HTMLResponse:
        start, end = week_range(week)
        result = report(store, week)
        return TEMPLATES.TemplateResponse(
            request, "index.html",
            {"week": week, "result": result, "entries": store.list_entries(start, end),
             "projects": store.list_projects(), "today": date.today().isoformat(),
             "error": error, "message": message},
        )

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request, week: str = "", error: str = "", message: str = "") -> HTMLResponse:
        try:
            return render(request, week or current_week(), error, message)
        except ValueError:
            return render(request, current_week(), "周号不合法", message)

    @app.post("/log")
    def do_log(
        text: str = Form(...), day: str = Form(""), start: str = Form("540")
    ) -> RedirectResponse:
        d = date.fromisoformat(day) if day else date.today()
        try:
            _, data = book(store, settings, text, d, int(start), llm)
        except ValueError as exc:
            return RedirectResponse(url=f"/?week={current_week()}&error={exc}", status_code=303)
        return RedirectResponse(
            url=f"/?week={d.strftime('%G-W%V')}&message=已入账 {data['minutes']} 分钟",
            status_code=303,
        )

    @app.get("/bill.csv", response_class=PlainTextResponse)
    def export_bill(week: str = "") -> PlainTextResponse:
        w = week or current_week()
        start, end = week_range(w)
        return PlainTextResponse(bill_csv(store, start, end), media_type="text/csv; charset=utf-8")

    @app.get("/report.md", response_class=PlainTextResponse)
    def export_report(week: str = "") -> PlainTextResponse:
        return PlainTextResponse(compose(store, week or current_week()), media_type="text/markdown")

    @app.get("/health")
    def health() -> dict[str, object]:
        return {"status": "ok", "entries": len(store.list_entries())}

    return app


def app_factory(settings: Settings | None = None) -> FastAPI:
    if settings is None:
        from ..config import settings as default_settings

        settings = default_settings
    return create_app(settings)

