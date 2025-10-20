# Task Management App

A lightweight task manager with both a command-line interface and a browser-based experience backed by a JSON datastore.

## Features

- Add tasks with optional descriptions.
- List pending or completed tasks with timestamps.
- Mark tasks as completed, delete them, or clear all completed tasks.
- Zero-dependency web UI powered by Python's built-in WSGI server.
- Persist tasks to `tasks.json` for easy portability.

## Requirements

- Python 3.9+
- (Optional) `pytest` for running the automated test suite.

## Running the web app

1. Ensure you are in the project directory.
2. Launch the development server:

   ```bash
   python web_app.py
   ```

   By default the app listens on `http://127.0.0.1:5000`. Visit that URL in your browser to manage tasks.

Tasks are stored in `tasks.json` next to the application. You can change the storage location by instantiating `TaskManagerWebApp` with a different `storage_path`.

## Using the CLI

The CLI stores tasks in `tasks.json` in the project directory. The file is created automatically on first use.

### Add a task

```bash
python task_manager.py add "Buy groceries" -d "Milk, eggs, bread"
```

### List tasks

```bash
python task_manager.py list        # Pending tasks only
python task_manager.py list --all  # Include completed tasks
```

### Complete a task

```bash
python task_manager.py complete 0
```

### Delete a task

```bash
python task_manager.py delete 0
```

### Clear completed tasks

```bash
python task_manager.py clear
```

## Testing

Run the unit tests with:

```bash
pytest
```
