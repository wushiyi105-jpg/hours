from __future__ import annotations

from hours.domain.models import Budget
from hours.domain.rules.budget import check


def test_warn_at_80_percent():
    findings = check([Budget(1, 1, "hours", 10)], {1: 8.5}, {})
    assert findings[0].rule_id == "budget.warn"


def test_over_at_100_percent():
    findings = check([Budget(1, 1, "hours", 10)], {1: 11}, {})
    assert findings[0].rule_id == "budget.over"


def test_amount_budget_independent():
    findings = check([Budget(1, 1, "amount", 1000)], {1: 1}, {1: 1200})
    assert findings[0].rule_id == "budget.over"


def test_under_threshold_silent():
    assert check([Budget(1, 1, "hours", 10)], {1: 3}, {}) == []
