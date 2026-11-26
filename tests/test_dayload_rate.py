from __future__ import annotations

from datetime import date

from hours.domain.models import Entry, Project
from hours.domain.rules.dayload import long_days
from hours.domain.rules.rate import missing


def test_long_day_flagged():
    entries = [Entry(1, 1, date(2026, 11, 23), 480, 600, ""), Entry(2, 1, date(2026, 11, 23), 1080, 600, "")]
    assert long_days(entries)[0].rule_id == "entry.long_day"


def test_normal_day_silent():
    assert long_days([Entry(1, 1, date(2026, 11, 23), 540, 480, "")]) == []


def test_missing_rate_flagged():
    findings = missing([Project(1, "免费项目", "", 0.0), Project(2, "有费率", "", 300.0)])
    assert findings[0].rule_id == "rate.missing"
    assert len(findings) == 1
