"""端口：app 实际调用的方法集合，实现见 adapters。"""

from __future__ import annotations

from datetime import date
from typing import Any, Protocol, runtime_checkable

from ..domain.models import Budget, Entry, Project


@runtime_checkable
class StorePort(Protocol):
    def list_projects(self) -> list[Project]: ...

    def add_entry(
        self, project_id: int, day: date, start: int, minutes: int, note: str, confidence: float
    ) -> int: ...

    def list_entries(self, start: date | None = None, end: date | None = None) -> list[Entry]: ...

    def list_budgets(self) -> list[Budget]: ...

    def enqueue(self, idem_key: str, kind: str, payload: str, due_on: date) -> bool: ...
    def due_jobs(self, today: date) -> list[Any]: ...
    def finish_job(self, job_id: int, ok: bool, error: str = "") -> None: ...


@runtime_checkable
class LLMPort(Protocol):
    def write(self, system: str, facts: str) -> str: ...


@runtime_checkable
class NotifierPort(Protocol):
    def send(self, text: str) -> bool: ...
