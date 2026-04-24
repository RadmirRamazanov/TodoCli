from __future__ import annotations

import argparse
import sys
from typing import Sequence

from . import __version__
from .models import Task
from .storage import Storage


def _format_task(task: Task) -> str:
    mark = "[x]" if task.done else "[ ]"
    return f"{task.id:>3}. {mark} {task.title}  ({task.created_at})"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="todo",
        description="Simple command-line todo manager.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--file",
        dest="file",
        default=None,
        help="Path to the tasks JSON file (overrides TODO_FILE env var).",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    p_add = subparsers.add_parser("add", help="Add a new task")
    p_add.add_argument("title", nargs="+", help="Task title")

    p_list = subparsers.add_parser("list", help="List tasks")
    p_list.add_argument(
        "--pending",
        action="store_true",
        help="Show only pending (not completed) tasks",
    )

    p_done = subparsers.add_parser("done", help="Mark a task as done")
    p_done.add_argument("id", type=int, help="Task id")

    p_remove = subparsers.add_parser("remove", help="Remove a task")
    p_remove.add_argument("id", type=int, help="Task id")

    subparsers.add_parser("clear", help="Remove all tasks")

    return parser


def run(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    storage = Storage(path=args.file)

    if args.command == "add":
        title = " ".join(args.title)
        try:
            task = storage.add(title)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        print(f"Added task #{task.id}: {task.title}")
        return 0

    if args.command == "list":
        tasks = storage.list(show_all=not args.pending)
        if not tasks:
            print("No tasks yet. Use `todo add <title>` to create one.")
            return 0
        for t in tasks:
            print(_format_task(t))
        return 0

    if args.command == "done":
        try:
            task = storage.complete(args.id)
        except KeyError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print(f"Completed task #{task.id}: {task.title}")
        return 0

    if args.command == "remove":
        try:
            task = storage.remove(args.id)
        except KeyError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print(f"Removed task #{task.id}: {task.title}")
        return 0

    if args.command == "clear":
        count = storage.clear()
        print(f"Removed {count} task(s).")
        return 0

    parser.print_help()
    return 2


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
