from io import BytesIO
from pathlib import Path
from typing import Dict, Iterable, Tuple
from urllib.parse import urlencode, urlsplit

import pytest

from task_manager import TaskManager
from web_app import TaskManagerWebApp


def call_app(app, method: str, path: str, data: Dict[str, str] | None = None) -> Tuple[str, Dict[str, str], bytes]:
    split = urlsplit(path)
    environ = {
        "REQUEST_METHOD": method,
        "PATH_INFO": split.path or "/",
        "QUERY_STRING": split.query,
        "wsgi.input": BytesIO(),
        "CONTENT_LENGTH": "0",
        "CONTENT_TYPE": "application/x-www-form-urlencoded",
        "SERVER_NAME": "testserver",
        "SERVER_PORT": "80",
        "SERVER_PROTOCOL": "HTTP/1.1",
    }

    if method == "POST":
        encoded = urlencode(data or {}).encode()
        environ["wsgi.input"] = BytesIO(encoded)
        environ["CONTENT_LENGTH"] = str(len(encoded))

    status_headers: Dict[str, Iterable] = {}

    def start_response(status: str, headers: Iterable[Tuple[str, str]]) -> None:
        status_headers["status"] = status
        status_headers["headers"] = dict(headers)

    body = b"".join(app(environ, start_response))
    return status_headers["status"], status_headers["headers"], body


@pytest.fixture
def web_client(tmp_path: Path) -> Tuple[TaskManagerWebApp, Path]:
    storage = tmp_path / "tasks.json"
    app = TaskManagerWebApp(storage_path=storage)
    return app, storage


def test_add_task_via_web(web_client: Tuple[TaskManagerWebApp, Path]) -> None:
    app, storage = web_client

    status, headers, _ = call_app(
        app,
        "POST",
        "/tasks",
        {"title": "Write docs", "description": "Update README"},
    )
    assert status.startswith("303")
    assert headers["Location"].startswith("/?message=")

    follow_status, _, body = call_app(app, "GET", headers["Location"])
    assert follow_status.startswith("200")
    assert b"Task added successfully" in body
    assert b"Write docs" in body

    manager = TaskManager(storage_path=storage)
    tasks = manager.list_tasks()
    assert len(tasks) == 1
    assert tasks[0].description == "Update README"


def test_complete_and_delete_task(web_client: Tuple[TaskManagerWebApp, Path]) -> None:
    app, storage = web_client
    manager = TaskManager(storage_path=storage)
    manager.add_task("Ship feature")

    status, headers, _ = call_app(app, "POST", "/tasks/0/complete")
    assert status.startswith("303")
    assert headers["Location"].startswith("/?message=")

    manager = TaskManager(storage_path=storage)
    assert manager.list_tasks()[0].completed

    status, headers, _ = call_app(app, "POST", "/tasks/0/delete")
    assert status.startswith("303")

    manager = TaskManager(storage_path=storage)
    assert manager.list_tasks() == []


def test_clear_completed_tasks(web_client: Tuple[TaskManagerWebApp, Path]) -> None:
    app, storage = web_client
    manager = TaskManager(storage_path=storage)
    manager.add_task("Done task")
    manager.add_task("Pending task")
    manager.complete_task(0)

    status, headers, _ = call_app(app, "POST", "/tasks/clear-completed")
    assert status.startswith("303")
    assert headers["Location"].startswith("/?message=")

    manager = TaskManager(storage_path=storage)
    tasks = manager.list_tasks()
    assert len(tasks) == 1
    assert tasks[0].title == "Pending task"


def test_validation_error_for_empty_title(web_client: Tuple[TaskManagerWebApp, Path]) -> None:
    app, _ = web_client

    status, headers, _ = call_app(app, "POST", "/tasks", {"title": "  "})
    assert status.startswith("303")
    assert headers["Location"].startswith("/?error=")

    follow_status, _, body = call_app(app, "GET", headers["Location"])
    assert follow_status.startswith("200")
    assert b"Task title is required" in body
