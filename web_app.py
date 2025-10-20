"""WSGI web application for the task manager."""
from __future__ import annotations

import html
from http import HTTPStatus
from io import BytesIO
from pathlib import Path
from typing import Callable, Iterable, Tuple
from urllib.parse import parse_qs, urlencode
from wsgiref.simple_server import make_server
from wsgiref.util import setup_testing_defaults

from task_manager import TASKS_FILE, Task, TaskManager

ResponseBody = Iterable[bytes]
StartResponse = Callable[[str, list[Tuple[str, str]]], Callable[..., None]]


def _format_datetime(value: str | None) -> str:
    if not value:
        return ""
    return html.escape(value.replace("T", " "))


def _read_post_data(environ: dict) -> dict[str, str]:
    try:
        size = int(environ.get("CONTENT_LENGTH", "0") or "0")
    except ValueError:
        size = 0
    data = environ.get("wsgi.input", BytesIO()).read(size)
    parsed = parse_qs(data.decode())
    return {key: values[0] for key, values in parsed.items() if values}


class TaskManagerWebApp:
    """Minimal WSGI application exposing the task manager via HTTP."""

    def __init__(self, storage_path: Path | None = None) -> None:
        self.storage_path = Path(storage_path) if storage_path else TASKS_FILE

    # -- WSGI protocol -----------------------------------------------------
    def __call__(self, environ: dict, start_response: StartResponse) -> ResponseBody:
        setup_testing_defaults(environ)
        method = environ["REQUEST_METHOD"].upper()
        path = environ["PATH_INFO"] or "/"

        if method == "GET" and path == "/":
            return self._handle_index(environ, start_response)
        if method == "GET" and path == "/static/styles.css":
            return self._handle_static(start_response)
        if method == "POST" and path == "/tasks":
            return self._handle_add(environ, start_response)
        if method == "POST" and path.endswith("/complete"):
            return self._handle_complete(path, start_response)
        if method == "POST" and path.endswith("/delete"):
            return self._handle_delete(path, start_response)
        if method == "POST" and path == "/tasks/clear-completed":
            return self._handle_clear(start_response)

        start_response(
            f"{HTTPStatus.NOT_FOUND.value} {HTTPStatus.NOT_FOUND.phrase}",
            [("Content-Type", "text/plain; charset=utf-8")],
        )
        return [b"Not found"]

    # -- HTTP handlers -----------------------------------------------------
    def _handle_index(self, environ: dict, start_response: StartResponse) -> ResponseBody:
        query = parse_qs(environ.get("QUERY_STRING", ""))
        message = query.get("message", [""])[0]
        error = query.get("error", [""])[0]

        manager = TaskManager(storage_path=self.storage_path)
        tasks = manager.list_tasks()
        active_count = len([task for task in tasks if not task.completed])
        completed_count = len(tasks) - active_count

        alerts = []
        if message:
            alerts.append(f'<div class="alert alert-success">{html.escape(message)}</div>')
        if error:
            alerts.append(f'<div class="alert alert-error">{html.escape(error)}</div>')
        alerts_html = "".join(alerts)
        alerts_wrapper = f'<div class="alerts">{alerts_html}</div>' if alerts else ""

        task_items = "".join(self._render_task(task, index) for index, task in enumerate(tasks))
        if task_items:
            task_section = f'<ul class="task-list">{task_items}</ul>'
        else:
            task_section = '<p class="empty">No tasks yet. Add your first task above.</p>'

        clear_button = (
            '<form method="post" action="/tasks/clear-completed" class="clear-form">'
            '<button type="submit">Clear completed tasks</button>'
            "</form>"
        ) if completed_count else ""

        body = f"""
<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\">
    <title>Task Manager</title>
    <link rel=\"stylesheet\" href=\"/static/styles.css\">
  </head>
  <body>
    <main class=\"layout\">
      <header>
        <h1>Task Manager</h1>
        <p class=\"subtitle\">Track your tasks, complete them, and stay organized.</p>
      </header>
      {alerts_wrapper}
      <section class=\"panel\">
        <h2>Add a task</h2>
        <form method=\"post\" action=\"/tasks\" class=\"add-form\">
          <label for=\"title\">Title</label>
          <input type=\"text\" id=\"title\" name=\"title\" placeholder=\"e.g. Buy groceries\" required>
          <label for=\"description\">Description</label>
          <textarea id=\"description\" name=\"description\" rows=\"3\" placeholder=\"Optional details\"></textarea>
          <button type=\"submit\">Add task</button>
        </form>
      </section>
      <section class=\"panel\">
        <div class=\"panel-header\">
          <h2>Tasks ({len(tasks)})</h2>
          <span>{active_count} open</span>
        </div>
        {task_section}
        {clear_button}
      </section>
    </main>
  </body>
</html>
"""
        encoded = body.encode("utf-8")
        start_response(
            f"{HTTPStatus.OK.value} {HTTPStatus.OK.phrase}",
            [
                ("Content-Type", "text/html; charset=utf-8"),
                ("Content-Length", str(len(encoded))),
            ],
        )
        return [encoded]

    def _handle_static(self, start_response: StartResponse) -> ResponseBody:
        css_path = Path("static/styles.css")
        data = css_path.read_bytes() if css_path.exists() else b""
        start_response(
            f"{HTTPStatus.OK.value} {HTTPStatus.OK.phrase}",
            [
                ("Content-Type", "text/css; charset=utf-8"),
                ("Content-Length", str(len(data))),
            ],
        )
        return [data]

    def _handle_add(self, environ: dict, start_response: StartResponse) -> ResponseBody:
        data = _read_post_data(environ)
        title = data.get("title", "").strip()
        description = data.get("description", "").strip()
        if not title:
            return self._redirect(start_response, error="Task title is required.")

        manager = TaskManager(storage_path=self.storage_path)
        manager.add_task(title, description=description)
        return self._redirect(start_response, message="Task added successfully.")

    def _handle_complete(self, path: str, start_response: StartResponse) -> ResponseBody:
        index = self._extract_index(path, "complete")
        manager = TaskManager(storage_path=self.storage_path)
        try:
            manager.complete_task(index)
        except ValueError:
            return self._redirect(start_response, error="Unable to complete the selected task.")
        return self._redirect(start_response, message="Task marked as complete.")

    def _handle_delete(self, path: str, start_response: StartResponse) -> ResponseBody:
        index = self._extract_index(path, "delete")
        manager = TaskManager(storage_path=self.storage_path)
        try:
            manager.delete_task(index)
        except ValueError:
            return self._redirect(start_response, error="Unable to delete the selected task.")
        return self._redirect(start_response, message="Task deleted.")

    def _handle_clear(self, start_response: StartResponse) -> ResponseBody:
        manager = TaskManager(storage_path=self.storage_path)
        manager.clear_completed()
        return self._redirect(start_response, message="Completed tasks cleared.")

    # -- Helpers -----------------------------------------------------------
    def _redirect(self, start_response: StartResponse, *, message: str = "", error: str = "") -> ResponseBody:
        params = {key: value for key, value in (("message", message), ("error", error)) if value}
        location = "/"
        if params:
            location += f"?{urlencode(params)}"
        start_response(
            f"{HTTPStatus.SEE_OTHER.value} {HTTPStatus.SEE_OTHER.phrase}",
            [("Location", location)],
        )
        return [b""]

    def _extract_index(self, path: str, action: str) -> int:
        try:
            _, _, index_part, _ = path.split("/", 3)
            return int(index_part)
        except (ValueError, IndexError):
            raise ValueError(f"Invalid {action} path: {path}") from None

    def _render_task(self, task: Task, index: int) -> str:
        classes = "task completed" if task.completed else "task"
        description = (
            f'<p class="task-description">{html.escape(task.description)}</p>'
            if task.description
            else ""
        )
        completed = (
            f'<span>Completed {_format_datetime(task.completed_at)}</span>'
            if task.completed and task.completed_at
            else ""
        )
        disabled = " disabled" if task.completed else ""
        return f"""
<li class=\"{classes}\">
  <div class=\"task-main\">
    <div class=\"task-header\">
      <span class=\"task-index\">#{index + 1}</span>
      <p class=\"task-title\">{html.escape(task.title)}</p>
    </div>
    {description}
    <div class=\"task-meta\">
      <span>Created {_format_datetime(task.created_at)}</span>
      {completed}
    </div>
  </div>
  <div class=\"task-actions\">
    <form method=\"post\" action=\"/tasks/{index}/complete\">
      <button type=\"submit\"{disabled}>Complete</button>
    </form>
    <form method=\"post\" action=\"/tasks/{index}/delete\">
      <button type=\"submit\" class=\"danger\">Delete</button>
    </form>
  </div>
</li>
"""

    def run(self, host: str = "127.0.0.1", port: int = 5000) -> None:
        """Start a development server for the application."""
        with make_server(host, port, self) as httpd:
            print(f"Serving on http://{host}:{port}")
            httpd.serve_forever()


def main() -> None:
    TaskManagerWebApp().run()


if __name__ == "__main__":
    main()
