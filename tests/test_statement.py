"""新功能：月底账单 CSV + 邮件正文。"""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from hours.iface.cli import app


def test_seed_has_three_projects_and_thirty_one_entries() -> None:
    data = json.loads((Path(__file__).resolve().parents[1] / "data" / "seed.json").read_text(encoding="utf-8"))
    assert len(data["projects"]) == 3
    assert len(data["entries"]) == 31


def test_statement_writes_csv_and_email(tmp_path) -> None:
    runner = CliRunner()
    db = str(tmp_path / "hours.db")
    assert runner.invoke(app, ["seed", "--db", db]).exit_code == 0
    out = tmp_path / "账单.csv"
    result = runner.invoke(app, ["statement", "--db", db, "--month", "2026-11", "--out", str(out)])
    assert result.exit_code == 0
    csv = out.read_text(encoding="utf-8")
    mail = out.with_suffix(".md").read_text(encoding="utf-8")
    assert csv.splitlines()[0] == "项目,客户,工时,费率,金额,税率,税额,含税合计"
    assert "合计" in csv
    assert "工时账单" in mail and "含税" in mail
    assert "青禾 SaaS 改版" in mail
