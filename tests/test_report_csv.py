from __future__ import annotations

from datetime import date

from hours.adapters.export import bill_csv
from hours.app.run import compose, report


def test_report_totals_match_csv(store, projects):
    store.add_entry(projects["青禾 SaaS 改版"], date(2026, 11, 23), 540, 240, "", 0.9)
    store.add_entry(projects["远山数据看板"], date(2026, 11, 24), 600, 180, "", 0.9)
    result = report(store, "2026-W48")
    csv = bill_csv(store, date(2026, 11, 23), date(2026, 11, 29))
    assert result.report.minutes == 420
    assert f"{result.report.amount:.2f}" in csv.splitlines()[-1]


def test_overlap_and_budget_in_report(store, projects):
    store.add_budget(projects["青禾 SaaS 改版"], "hours", 5)
    store.add_entry(projects["青禾 SaaS 改版"], date(2026, 11, 23), 540, 240, "", 0.9)
    store.add_entry(projects["青禾 SaaS 改版"], date(2026, 11, 23), 600, 120, "", 0.9)
    result = report(store, "2026-W48")
    ids = {f.rule_id for f in result.report.findings}
    assert "overlap.entries" in ids
    assert "budget.over" in ids


def test_compose_renders_table(store, projects):
    store.add_entry(projects["青禾 SaaS 改版"], date(2026, 11, 23), 540, 120, "", 0.9)
    text = compose(store, "2026-W48")
    assert "# 工时周报 2026-W48" in text
    assert "120 分钟" in text

