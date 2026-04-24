from __future__ import annotations

from pathlib import Path

import pytest

from todo_cli.cli import run


@pytest.fixture
def tasks_file(tmp_path: Path) -> Path:
    return tmp_path / "tasks.json"


def test_cli_add_and_list(tasks_file: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert run(["--file", str(tasks_file), "add", "buy", "milk"]) == 0
    assert run(["--file", str(tasks_file), "list"]) == 0
    out = capsys.readouterr().out
    assert "Added task #1: buy milk" in out
    assert "buy milk" in out


def test_cli_done_and_pending_filter(
    tasks_file: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run(["--file", str(tasks_file), "add", "task one"])
    run(["--file", str(tasks_file), "add", "task two"])
    run(["--file", str(tasks_file), "done", "1"])
    capsys.readouterr()  # clear

    assert run(["--file", str(tasks_file), "list", "--pending"]) == 0
    out = capsys.readouterr().out
    assert "task two" in out
    assert "task one" not in out


def test_cli_remove(tasks_file: Path, capsys: pytest.CaptureFixture[str]) -> None:
    run(["--file", str(tasks_file), "add", "delete me"])
    capsys.readouterr()
    assert run(["--file", str(tasks_file), "remove", "1"]) == 0
    out = capsys.readouterr().out
    assert "Removed task #1" in out


def test_cli_done_unknown_id_returns_error(
    tasks_file: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = run(["--file", str(tasks_file), "done", "123"])
    assert code == 1
    err = capsys.readouterr().err
    assert "not found" in err


def test_cli_clear(tasks_file: Path, capsys: pytest.CaptureFixture[str]) -> None:
    run(["--file", str(tasks_file), "add", "a"])
    run(["--file", str(tasks_file), "add", "b"])
    capsys.readouterr()
    assert run(["--file", str(tasks_file), "clear"]) == 0
    out = capsys.readouterr().out
    assert "Removed 2 task(s)" in out


def test_cli_list_empty_message(
    tasks_file: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(["--file", str(tasks_file), "list"]) == 0
    out = capsys.readouterr().out
    assert "No tasks yet" in out
