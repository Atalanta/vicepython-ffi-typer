# Getting Started

We'll walk you through building your first CLI with vicepython-ffi-typer. You'll create a simple task manager that demonstrates the core concepts: command handlers, Result types, error handling, and testing.

Time: 15 minutes

## Prerequisites

- Python ≥3.12 installed
- Basic familiarity with VicePython's `Result` and `Option` types
- `uv` package manager installed

## Step 1: Create Your Project

```bash
mkdir mytasks
cd mytasks
uv init
uv add vicepython-ffi-typer
```

## Step 2: Define an Error Type

Create `src/mytasks/errors.py`:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class TaskError:
    """Error type for task operations."""
    message: str

    def __str__(self) -> str:
        return f"Error: {self.message}"
```

We use frozen dataclasses because they're immutable and simple. The `__str__()` method provides the message users see when something fails.

## Step 3: Write Your First Command

Create `src/mytasks/cli.py`:

```python
from vicepython_core import Ok, Err, Result
from vicepython_ffi_typer import TypedTyper

from .errors import TaskError

app = TypedTyper()

@app.command_result()
def add(task: str) -> Result[None, TaskError]:
    """Add a new task."""
    if not task.strip():
        return Err(TaskError("Task description can't be empty"))

    # In a real app, you'd save to a database or file here
    print(f"Added task: {task}")
    return Ok(None)
```

Let's break down what's happening:
- We create a `TypedTyper` app instance
- We decorate our function with `@app.command_result()`
- The function returns `Result[None, TaskError]`
- Validation errors return `Err(TaskError(...))`
- Success prints output directly and returns `Ok(None)`

## Step 4: Add the Main Entry Point

Create `src/mytasks/__main__.py`:

```python
import sys
from vicepython_ffi_typer import run
from .cli import app

sys.exit(run(app, sys.argv))
```

This is the **only** place where exit codes matter. We call `run(app, sys.argv)` and pass its return value to `sys.exit()`.

## Step 5: Run Your CLI

```bash
uv run python -m mytasks add "Write documentation"
```

Output:
```
Added task: Write documentation
```

Try with an empty task:
```bash
uv run python -m mytasks add ""
```

Output to stderr:
```
Error: Task description can't be empty
```

Check the exit code (`echo $?` on Unix or `echo %ERRORLEVEL%` on Windows): it'll be 1.

## Step 6: Add a Command with Optional Parameters

Add a `list` command to `src/mytasks/cli.py`:

```python
from vicepython_core import Option, Some, Nothing
from vicepython_core.option import option_from_optional

@app.command_result()
def list_tasks(
    filter: str | None = None,
) -> Result[None, TaskError]:
    """List all tasks, optionally filtered."""
    # Convert Optional → Option at boundary
    filter_opt: Option[str] = option_from_optional(filter)

    # In a real app, you'd query a database or file here
    tasks = ["Write docs", "Add tests", "Review PR"]

    match filter_opt:
        case Some(keyword):
            filtered = [t for t in tasks if keyword.lower() in t.lower()]
            for task in filtered:
                print(f"- {task}")
        case Nothing():
            for task in tasks:
                print(f"- {task}")

    return Ok(None)
```

The pattern here: CLI signatures can use `str | None` for optional parameters. We convert them immediately to `Option[T]` and use pattern matching to handle `Some` / `Nothing` cases.

Run it:
```bash
uv run python -m mytasks list-tasks
uv run python -m mytasks list-tasks --filter docs
```

## Step 7: Write Tests

Create `tests/test_cli.py`:

```python
import pytest
from vicepython_ffi_typer import run
from mytasks.cli import app

def test_add_success(capsys):
    """Adding a valid task succeeds with exit code 0."""
    code = run(app, ["prog", "add", "Buy milk"])

    assert code == 0
    captured = capsys.readouterr()
    assert "Added task: Buy milk" in captured.out
    assert captured.err == ""

def test_add_empty_fails(capsys):
    """Adding an empty task fails with exit code 1."""
    code = run(app, ["prog", "add", ""])

    assert code == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Task description can't be empty" in captured.err

def test_list_with_filter(capsys):
    """List command accepts filter parameter."""
    code = run(app, ["prog", "list-tasks", "--filter", "docs"])

    assert code == 0
    captured = capsys.readouterr()
    assert "Write docs" in captured.out
```

Testing rules:
- Always test via `run(app, argv)`
- Never call decorated command functions directly for CLI behavior tests
- Use pytest's `capsys` fixture to verify stdout/stderr
- First argv element is the program name (we use `"prog"`)

Run tests:
```bash
uv run pytest
```

## What You Learned

1. **Command Structure**: Functions decorated with `@app.command_result()` return `Result[None, E]`
2. **Error Handling**: Return `Err(e)` for domain errors; `run()` prints them to stderr
3. **Success Output**: Print directly in command handlers; return `Ok(None)`
4. **Optional Parameters**: Use `str | None` in signatures, convert to `Option[T]` immediately
5. **Testing**: Invoke via `run(app, argv)` and verify exit codes + output

## Next Steps

- [User Guide](./USER_GUIDE.md) — Task-focused how-to guides
- [Core Concepts](./CONCEPTS.md) — Understand error types, exit codes, and testing philosophy
- [API Reference](./API_REFERENCE.md) — Complete API specifications
