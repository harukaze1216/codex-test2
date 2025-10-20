"""Simple task management CLI application."""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import List, Optional

TASKS_FILE = Path("tasks.json")


@dataclass
class Task:
    """Represents a task in the task manager."""

    title: str
    description: str = ""
    completed: bool = False
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    completed_at: Optional[str] = None

    def complete(self) -> None:
        if not self.completed:
            self.completed = True
            self.completed_at = datetime.now(UTC).isoformat()


class TaskManager:
    """Manages loading, saving, and updating tasks."""

    def __init__(self, storage_path: Path = TASKS_FILE) -> None:
        self.storage_path = storage_path
        self.tasks: List[Task] = []
        self.load()

    def load(self) -> None:
        if self.storage_path.exists():
            with self.storage_path.open("r", encoding="utf-8") as f:
                raw_tasks = json.load(f)
            self.tasks = [Task(**task) for task in raw_tasks]
        else:
            self.tasks = []

    def save(self) -> None:
        with self.storage_path.open("w", encoding="utf-8") as f:
            json.dump([task.__dict__ for task in self.tasks], f, indent=2)

    def add_task(self, title: str, description: str = "") -> Task:
        task = Task(title=title, description=description)
        self.tasks.append(task)
        self.save()
        return task

    def list_tasks(self, show_completed: bool = True) -> List[Task]:
        if show_completed:
            return list(self.tasks)
        return [task for task in self.tasks if not task.completed]

    def complete_task(self, index: int) -> Task:
        try:
            task = self.tasks[index]
        except IndexError as exc:
            raise ValueError("Invalid task index") from exc
        task.complete()
        self.save()
        return task

    def delete_task(self, index: int) -> Task:
        try:
            task = self.tasks.pop(index)
        except IndexError as exc:
            raise ValueError("Invalid task index") from exc
        self.save()
        return task

    def clear_completed(self) -> None:
        self.tasks = [task for task in self.tasks if not task.completed]
        self.save()


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Task management CLI")
    subparsers = parser.add_subparsers(dest="command")

    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("title", help="Title of the task")
    add_parser.add_argument("-d", "--description", default="", help="Task description")

    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument("-a", "--all", action="store_true", help="Show completed tasks as well")

    complete_parser = subparsers.add_parser("complete", help="Mark a task as completed")
    complete_parser.add_argument("index", type=int, help="Index of the task to complete")

    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("index", type=int, help="Index of the task to delete")

    subparsers.add_parser("clear", help="Clear completed tasks")

    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:
    manager = TaskManager()
    args = parse_args(argv)

    if args.command == "add":
        task = manager.add_task(args.title, description=args.description)
        print(f"Added task: {task.title}")
    elif args.command == "list":
        tasks = manager.list_tasks(show_completed=args.all)
        if not tasks:
            print("No tasks found.")
        for index, task in enumerate(tasks):
            status = "✓" if task.completed else "✗"
            description = f" - {task.description}" if task.description else ""
            print(f"{index}: [{status}] {task.title}{description}")
    elif args.command == "complete":
        try:
            task = manager.complete_task(args.index)
        except ValueError as error:
            print(error)
        else:
            print(f"Completed task: {task.title}")
    elif args.command == "delete":
        try:
            task = manager.delete_task(args.index)
        except ValueError as error:
            print(error)
        else:
            print(f"Deleted task: {task.title}")
    elif args.command == "clear":
        manager.clear_completed()
        print("Cleared completed tasks.")
    else:
        print("No command provided. Use -h for help.")


if __name__ == "__main__":
    main()
