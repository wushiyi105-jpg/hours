"""真实内存 Store 跑 report：不建 SQLite，mypy 校验 StorePort。"""

from __future__ import annotations

from datetime import date
from typing import Any

from hours.app.run import report
from hours.domain.models import Budget, Entry, Project
from hours.ports import StorePort


class InMemoryStore:
    def list_projects(self) -> list[Project]:
        return []

    def add_entry(
        self, project_id: int, day: date, start: int, minutes: int, note: str, confidence: float
    ) -> int:
        return 1

    def list_entries(self, start: date | None = None, end: date | None = None) -> list[Entry]:
        return []

    def list_budgets(self) -> list[Budget]:
        return []

    def enqueue(self, idem_key: str, kind: str, payload: str, due_on: date) -> bool:
        return True

    def due_jobs(self, today: date) -> list[Any]:
        return []

    def finish_job(self, job_id: int, ok: bool, error: str = "") -> None:
        return None


def test_report_with_memory_store() -> None:
    store: StorePort = InMemoryStore()
    out = report(store, "2026-W01")
    assert out.report.week == "2026-W01"
