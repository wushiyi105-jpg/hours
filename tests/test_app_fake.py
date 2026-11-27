"""主用例只依赖 ports：用 MagicMock 内存假实现，不建 SQLite 文件。"""

from __future__ import annotations

from unittest.mock import MagicMock

from hours.app.run import report
from hours.ports import StorePort


def test_main_path_with_memory_store(tmp_path) -> None:
    store = MagicMock(spec=StorePort)
    
    out = report(store, "2026-W01")
    assert out is not None
    assert not (tmp_path / "app.db").exists()
