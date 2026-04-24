from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterable

from .models import Task


class Storage:
    """JSON-backed storage for tasks.

    The path to the data file is taken from the constructor argument or,
    if not provided, from the TODO_FILE environment variable.
    Defaults to ``~/.todo-cli/tasks.json``.
    """

    DEFAULT_PATH = Path.home() / ".todo-cli" / "tasks.json"

    def __init__(self, path: str | os.PathLike[str] | None = None) -> None:
        if path is None:
            env_path = os.environ.get("TODO_FILE")
            path = env_path if env_path else self.DEFAULT_PATH
        self.path = Path(path)

    def _ensure_file(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def load(self) -> list[Task]:
        self._ensure_file()
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8") or "[]")
        except json.JSONDecodeError:
            return []
        if not isinstance(raw, list):
            return []
        return [Task.from_dict(item) for item in raw]

    def save(self, tasks: Iterable[Task]) -> None:
        self._ensure_file()
        data = [t.to_dict() for t in tasks]
        self.path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def next_id(self, tasks: list[Task]) -> int:
        return (max((t.id for t in tasks), default=0)) + 1

    def add(self, title: str) -> Task:
        title = title.strip()
        if not title:
            raise ValueError("Task title must not be empty")
        tasks = self.load()
        task = Task(id=self.next_id(tasks), title=title)
        tasks.append(task)
        self.save(tasks)
        return task

    def list(self, show_all: bool = True) -> list[Task]:
        tasks = self.load()
        if show_all:
            return tasks
        return [t for t in tasks if not t.done]

    def complete(self, task_id: int) -> Task:
        tasks = self.load()
        for t in tasks:
            if t.id == task_id:
                t.done = True
                self.save(tasks)
                return t
        raise KeyError(f"Task with id={task_id} not found")

    def remove(self, task_id: int) -> Task:
        tasks = self.load()
        for i, t in enumerate(tasks):
            if t.id == task_id:
                removed = tasks.pop(i)
                self.save(tasks)
                return removed
        raise KeyError(f"Task with id={task_id} not found")

    def clear(self) -> int:
        tasks = self.load()
        count = len(tasks)
        self.save([])
        return count
