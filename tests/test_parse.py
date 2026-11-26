from __future__ import annotations

from hours.domain.rules.parse import parse

NAMES = ["青禾 SaaS 改版", "远山数据看板"]


def test_half_day():
    project, minutes, conf = parse("今天上午都在青禾 SaaS 改版", NAMES)
    assert minutes == 240
    assert project == "青禾 SaaS 改版"
    assert conf >= 0.8


def test_hours_with_number():
    _, minutes, _ = parse("在远山数据看板做了 2 小时", NAMES)
    assert minutes == 120


def test_minutes_phrase():
    _, minutes, _ = parse("改文案 45 分钟", NAMES)
    assert minutes == 45


def test_unknown_project_lowers_confidence():
    project, _, conf = parse("改了个登录 3 小时", NAMES)
    assert project == ""
    assert conf <= 0.5
