"""本地拆条：中文口语里的时长与项目，先本地算，模型只补描述。"""

from __future__ import annotations

import re

HALF_DAY = 240
WORDS = {
    "一上午": 240,
    "一下午": 240,
    "半天": 240,
    "一整天": 480,
    "上午": 240,
    "下午": 240,
    "晚上": 180,
    "两小时": 120,
    "一小时": 60,
    "半小时": 30,
    "一个半小时": 90,
}
NUM = re.compile(r"(\d+(?:\.\d+)?)\s*(?:小时|h)")
MIN = re.compile(r"(\d+)\s*分钟")


def parse_minutes(text: str) -> tuple[int, float]:
    for word, minutes in WORDS.items():
        if word in text:
            return minutes, 0.8
    m = NUM.search(text)
    if m:
        return int(float(m.group(1)) * 60), 0.9
    m = MIN.search(text)
    if m:
        return int(m.group(1)), 0.9
    return 0, 0.0


def parse_project(text: str, names: list[str]) -> str:
    for name in names:
        if name in text:
            return name
    return ""


def parse(text: str, names: list[str]) -> tuple[str, int, float]:
    minutes, conf = parse_minutes(text)
    project = parse_project(text, names)
    if not project:
        conf = min(conf, 0.5)
    return project, minutes, conf

