"""每周五汇总提醒：一周一条，失败留 pending。"""

from __future__ import annotations

from datetime import date

from ..adapters.notify import WebhookNotifier
from ..adapters.store import SqliteStore
from ..config import Settings
from .run import compose


def enqueue_weekly(store: SqliteStore, week: str, due: date) -> bool:
    return store.enqueue(f"hours:{week}", "weekly_digest", week, due)


def run_due(store: SqliteStore, settings: Settings, today: date) -> int:
    notifier = WebhookNotifier(settings.webhook_url)
    sent = 0
    for job in store.due_jobs(today):
        text = compose(store, job.payload)
        ok = notifier.send(text)
        store.finish_job(job.id, ok, "" if ok else "推送失败")
        sent += int(ok)
    return sent
