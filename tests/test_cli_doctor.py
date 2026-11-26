from __future__ import annotations

from typer.testing import CliRunner

from hours.doctor import run_doctor
from hours.iface.cli import app


def test_doctor_green(settings):
    checks, ok = run_doctor(settings)
    assert ok is True


def test_cli_log_bad_project(tmp_path):
    runner = CliRunner()
    db = str(tmp_path / "c.db")
    res = runner.invoke(app, ["log", "--text", "写代码 2 小时", "--db", db])
    assert res.exit_code == 2


def test_cli_seed_then_report(tmp_path):
    runner = CliRunner()
    db = str(tmp_path / "c.db")
    assert runner.invoke(app, ["seed", "--db", db]).exit_code == 0
    res = runner.invoke(app, ["report", "--week", "2026-W48", "--db", db])
    assert res.exit_code == 0
    assert "overlap.entries" in res.output
