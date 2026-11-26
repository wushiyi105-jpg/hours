from __future__ import annotations

from datetime import date

from fastapi.testclient import TestClient

from hours.app.run import book
from hours.iface.web import create_app


def test_book_low_confidence_rejected(store, settings, projects):
    try:
        book(store, settings, "改了个登录 3 小时", date(2026, 11, 23), 540)
    except ValueError as exc:
        assert "置信度" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("should reject")


def test_book_valid_entry(store, settings, projects):
    entry_id, data = book(store, settings, "在青禾 SaaS 改版做了 3 小时", date(2026, 11, 23), 540)
    assert entry_id > 0
    assert data["minutes"] == 180


def test_web_log_and_export(store, settings, projects):
    client = TestClient(create_app(settings, store))
    assert client.get("/").status_code == 200
    resp = client.post("/log", data={"text": "在青禾 SaaS 改版做了 2 小时", "day": "2026-11-23",
                                     "start": "540"}, follow_redirects=False)
    assert resp.status_code == 303
    assert "青禾" in client.get("/bill.csv?week=2026-W48").text
