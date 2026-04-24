from __future__ import annotations

import json
from pathlib import Path

import pytest

from todo_cli.models import Task
from todo_cli.storage import Storage


@pytest.fixture
def storage(tmp_path: Path) -> Storage:
    return Storage(path=tmp_path / "tasks.json")


def test_load_empty_when_file_missing(storage: Storage) -> None:
    assert storage.load() == []
    assert storage.path.exists()


def test_add_creates_task_with_incremental_id(storage: Storage) -> None:
    t1 = storage.add("first task")
    t2 = storage.add("second task")
    assert t1.id == 1
    assert t2.id == 2
    assert t1.done is False
    assert storage.load()[0].title == "first task"


def test_add_empty_title_raises(storage: Storage) -> None:
    with pytest.raises(ValueError):
        storage.add("   ")


def test_complete_marks_task_done(storage: Storage) -> None:
    storage.add("write tests")
    storage.complete(1)
    tasks = storage.load()
    assert tasks[0].done is True


def test_complete_missing_id_raises(storage: Storage) -> None:
    with pytest.raises(KeyError):
        storage.complete(42)


def test_remove_deletes_task(storage: Storage) -> None:
    storage.add("a")
    storage.add("b")
    removed = storage.remove(1)
    assert removed.title == "a"
    remaining = storage.load()
    assert len(remaining) == 1
    assert remaining[0].title == "b"


def test_remove_missing_id_raises(storage: Storage) -> None:
    with pytest.raises(KeyError):
        storage.remove(999)


def test_list_pending_filters_done(storage: Storage) -> None:
    storage.add("a")
    storage.add("b")
    storage.complete(1)
    pending = storage.list(show_all=False)
    assert len(pending) == 1
    assert pending[0].title == "b"


def test_clear_removes_all_tasks(storage: Storage) -> None:
    storage.add("a")
    storage.add("b")
    count = storage.clear()
    assert count == 2
    assert storage.load() == []


def test_storage_uses_env_var(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    target = tmp_path / "from-env.json"
    monkeypatch.setenv("TODO_FILE", str(target))
    s = Storage()
    s.add("env task")
    assert target.exists()
    data = json.loads(target.read_text(encoding="utf-8"))
    assert data[0]["title"] == "env task"


def test_load_recovers_from_corrupted_file(tmp_path: Path) -> None:
    path = tmp_path / "tasks.json"
    path.write_text("not a valid json", encoding="utf-8")
    s = Storage(path=path)
    assert s.load() == []


def test_task_roundtrip_dict() -> None:
    t = Task(id=1, title="x")
    data = t.to_dict()
    restored = Task.from_dict(data)
    assert restored == t
