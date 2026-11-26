"""SQLite：projects / entries / budgets / jobs。"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from sqlalchemy import Date, Float, Integer, String, Text, inspect, select
from sqlalchemy.orm import Mapped, Session, mapped_column, sessionmaker

from ...domain.models import Budget, Entry, Project
from .base import Base, make_engine, make_session


class ProjectRow(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    client: Mapped[str] = mapped_column(String(80), default="")
    rate: Mapped[float] = mapped_column(Float, default=0.0)


class EntryRow(Base):
    __tablename__ = "entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, index=True)
    day: Mapped[date] = mapped_column(Date)
    start: Mapped[int] = mapped_column(Integer, default=540)
    minutes: Mapped[int] = mapped_column(Integer)
    note: Mapped[str] = mapped_column(Text, default="")
    confidence: Mapped[float] = mapped_column(Float, default=0.9)


class BudgetRow(Base):
    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, index=True)
    kind: Mapped[str] = mapped_column(String(12))
    limit: Mapped[float] = mapped_column(Float)


class JobRow(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    idem_key: Mapped[str] = mapped_column(String(80), unique=True)
    kind: Mapped[str] = mapped_column(String(24))
    payload: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(12), default="pending")
    due_on: Mapped[date] = mapped_column(Date)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str] = mapped_column(Text, default="")


class SqliteStore:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self.engine = make_engine(self.path)
        self.session: sessionmaker[Session] = make_session(self.engine)
        self.init_schema()

    def init_schema(self) -> None:
        Base.metadata.create_all(self.engine)

    def schema_ok(self) -> bool:
        return {"projects", "entries", "budgets", "jobs"} <= set(
            inspect(self.engine).get_table_names()
        )

    def summary(self) -> str:
        return f"{len(self.list_projects())} 个项目、{len(self.list_entries())} 条工时"

    def add_project(self, name: str, client: str, rate: float) -> int:
        with self.session() as s:
            row = ProjectRow(name=name, client=client, rate=rate)
            s.add(row)
            s.commit()
            return int(row.id)

    def list_projects(self) -> list[Project]:
        with self.session() as s:
            rows = s.scalars(select(ProjectRow)).all()
        return [Project(r.id, r.name, r.client, r.rate) for r in rows]

    def add_entry(
        self, project_id: int, day: date, start: int, minutes: int, note: str, confidence: float
    ) -> int:
        if not 0 < minutes <= 1440:
            raise ValueError("minutes 必须在 1-1440 之间")
        if not 0 <= start < 1440:
            raise ValueError("start 是当天第几分钟，0-1439")
        with self.session() as s:
            row = EntryRow(project_id=project_id, day=day, start=start, minutes=minutes,
                           note=note, confidence=confidence)
            s.add(row)
            s.commit()
            return int(row.id)

    def list_entries(self, start: date | None = None, end: date | None = None) -> list[Entry]:
        with self.session() as s:
            stmt = select(EntryRow)
            if start:
                stmt = stmt.where(EntryRow.day >= start)
            if end:
                stmt = stmt.where(EntryRow.day <= end)
            rows = s.scalars(stmt.order_by(EntryRow.day, EntryRow.start)).all()
        return [
            Entry(r.id, r.project_id, r.day, r.start, r.minutes, r.note, r.confidence) for r in rows
        ]

    def add_budget(self, project_id: int, kind: str, limit: float) -> int:
        if kind not in ("hours", "amount"):
            raise ValueError("kind 只能是 hours 或 amount")
        with self.session() as s:
            row = BudgetRow(project_id=project_id, kind=kind, limit=limit)
            s.add(row)
            s.commit()
            return int(row.id)

    def list_budgets(self) -> list[Budget]:
        with self.session() as s:
            rows = s.scalars(select(BudgetRow)).all()
        return [Budget(r.id, r.project_id, r.kind, r.limit) for r in rows]

    def enqueue(self, idem_key: str, kind: str, payload: str, due_on: date) -> bool:
        with self.session() as s:
            if s.scalar(select(JobRow).where(JobRow.idem_key == idem_key)):
                return False
            s.add(JobRow(idem_key=idem_key, kind=kind, payload=payload, due_on=due_on))
            s.commit()
            return True

    def due_jobs(self, today: date) -> list[JobRow]:
        with self.session() as s:
            return list(
                s.scalars(
                    select(JobRow).where(JobRow.status == "pending", JobRow.due_on <= today)
                ).all()
            )

    def finish_job(self, job_id: int, ok: bool, error: str = "") -> None:
        with self.session() as s:
            row = s.get(JobRow, job_id)
            if row is None:
                return
            row.status = "done" if ok else "pending"
            row.attempts += 1
            row.error = error
            s.commit()

