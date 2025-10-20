from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from task_manager import TaskManager


@pytest.fixture
def tmp_tasks_file(tmp_path: Path) -> Path:
    return tmp_path / "tasks.json"


def test_add_and_list_tasks(tmp_tasks_file: Path) -> None:
    manager = TaskManager(storage_path=tmp_tasks_file)
    manager.add_task("Test task", description="Details")

    tasks = manager.list_tasks()
    assert len(tasks) == 1
    assert tasks[0].title == "Test task"
    assert tasks[0].description == "Details"
    assert not tasks[0].completed


def test_complete_task(tmp_tasks_file: Path) -> None:
    manager = TaskManager(storage_path=tmp_tasks_file)
    manager.add_task("Complete me")

    manager.complete_task(0)
    tasks = manager.list_tasks()
    assert tasks[0].completed
    assert tasks[0].completed_at is not None


def test_delete_task(tmp_tasks_file: Path) -> None:
    manager = TaskManager(storage_path=tmp_tasks_file)
    manager.add_task("Delete me")

    manager.delete_task(0)
    assert manager.list_tasks() == []


def test_clear_completed(tmp_tasks_file: Path) -> None:
    manager = TaskManager(storage_path=tmp_tasks_file)
    manager.add_task("Completed task")
    manager.add_task("Incomplete task")
    manager.complete_task(0)

    manager.clear_completed()
    tasks = manager.list_tasks()
    assert len(tasks) == 1
    assert tasks[0].title == "Incomplete task"


def test_invalid_index_raises(tmp_tasks_file: Path) -> None:
    manager = TaskManager(storage_path=tmp_tasks_file)
    manager.add_task("Only task")

    with pytest.raises(ValueError):
        manager.complete_task(1)

    with pytest.raises(ValueError):
        manager.delete_task(1)
