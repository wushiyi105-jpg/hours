from __future__ import annotations

from datetime import date

from hours.domain.models import Entry
from hours.domain.rules.overlap import overlaps


def _e(id_, start, minutes, project=1, day="2026-11-23"):
    return Entry(id_, project, date.fromisoformat(day), start, minutes, "")


def test_overlapping_entries_flagged():
    findings = overlaps([_e(1, 540, 240), _e(2, 600, 120)])
    assert findings[0].rule_id == "overlap.entries"
    assert "120 分钟" in findings[0].message


def test_back_to_back_not_flagged():
    assert overlaps([_e(1, 540, 240), _e(2, 780, 60)]) == []


def test_different_project_not_flagged():
    assert overlaps([_e(1, 540, 240, 1), _e(2, 600, 120, 2)]) == []
