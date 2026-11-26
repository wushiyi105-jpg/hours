from __future__ import annotations

import pytest

from hours.adapters.store import SqliteStore
from hours.config import Settings


@pytest.fixture()
def store(tmp_path) -> SqliteStore:
    return SqliteStore(tmp_path / "t.db")


@pytest.fixture()
def settings(tmp_path) -> Settings:
    return Settings(db_path=tmp_path / "t.db", llm_api_key="", port=8002)


@pytest.fixture()
def projects(store):
    ids = {
        "青禾 SaaS 改版": store.add_project("青禾 SaaS 改版", "青禾设计", 320.0),
        "远山数据看板": store.add_project("远山数据看板", "远山科技", 260.0),
        "免费项目": store.add_project("免费项目", "", 0.0),
    }
    return ids
