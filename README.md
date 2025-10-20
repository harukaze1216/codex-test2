# Task Management CLI

A lightweight command-line application for managing tasks with persistent storage.

## Features

- Add tasks with optional descriptions.
- List pending tasks or all tasks.
- Mark tasks as completed and record completion timestamps.
- Delete tasks by index.
- Clear all completed tasks.

## Requirements

- Python 3.9+
- (Optional) `pytest` for running the automated test suite.

## Installation

1. Clone the repository and navigate to the project directory.
2. (Optional) Create a virtual environment and activate it.
3. Install development dependencies for testing:

   ```bash
   pip install pytest
   ```

## Usage

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
