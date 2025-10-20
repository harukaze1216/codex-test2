# Task Management App

A lightweight task manager with a command-line interface, a Python WSGI web server, and a static front-end that can be hosted on GitHub Pages.

## Features

- Add tasks with optional descriptions.
- List pending or completed tasks with timestamps.
- Mark tasks as completed, delete them, or clear all completed tasks.
- Zero-dependency web UI powered by Python's built-in WSGI server.
- Static single-page app that runs entirely in the browser and saves tasks to `localStorage`, making it ideal for GitHub Pages hosting.
- Persist tasks to `tasks.json` for easy portability when using the CLI or WSGI server.

## Requirements

- Python 3.9+
- (Optional) `pytest` for running the automated test suite.

## GitHub Pages deployment

The repository ships with a static web client located in the `docs/` directory. GitHub Pages can serve this directory without any build step.

1. Push the repository to GitHub.
2. Navigate to **Settings → Pages** in your repository.
3. Under **Build and deployment**, choose `Deploy from a branch`.
4. Select the `main` branch and the `/docs` folder, then click **Save**.
5. Wait for GitHub Pages to publish the site. Once complete, the hosted URL will run the task manager entirely in the browser, storing tasks in local storage.

To preview the static site locally, run a simple HTTP server and open `http://localhost:8000`:

```bash
cd docs
python -m http.server
```

## Running the Python web app

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
