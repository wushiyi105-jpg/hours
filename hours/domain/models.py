"""领域对象：条目、项目、预算、周报。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class Project:
    id: int
    name: str
    client: str
    rate: float


@dataclass(frozen=True)
class Entry:
    id: int
    project_id: int
    day: date
    start: int
    minutes: int
    note: str
    confidence: float = 0.9

    @property
    def end(self) -> int:
        return self.start + self.minutes


@dataclass(frozen=True)
class Budget:
    id: int
    project_id: int
    kind: str
    limit: float


@dataclass
class Finding:
    rule_id: str
    message: str
    penalty: int
    target: str = ""


@dataclass
class Report:
    week: str
    rows: list[tuple[str, str, float, float]] = field(default_factory=list)
    minutes: int = 0
    amount: float = 0.0
    findings: list[Finding] = field(default_factory=list)

    @property
    def penalty_total(self) -> int:
        return sum(f.penalty for f in self.findings)
