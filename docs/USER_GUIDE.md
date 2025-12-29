# User Guide

Task-focused guides for building CLIs with vicepython-ffi-typer. Each guide shows you how to accomplish a specific goal.

## Contents

- [Create an error type](#create-an-error-type)
- [Handle optional parameters](#handle-optional-parameters)
- [Test a successful command](#test-a-successful-command)
- [Test a failing command](#test-a-failing-command)
- [Build a multi-command app](#build-a-multi-command-app)
- [Add help text](#add-help-text)
- [Use Typer features directly](#use-typer-features-directly)
- [Handle file path arguments](#handle-file-path-arguments)
- [Use boolean flags](#use-boolean-flags)
- [Exit with a specific code](#exit-with-a-specific-code)

---

## Create an error type

Define an error type for your command's `Err()` returns.

**Steps:**

1. Create a frozen dataclass
2. Add fields for error details
3. Implement `__str__()` with a user-facing message

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class ValidationError:
    field: str
    reason: str

    def __str__(self) -> str:
        return f"Invalid {self.field}: {self.reason}"
```

**Use it in a command:**

```python
@app.command_result()
def create(name: str) -> Result[None, ValidationError]:
    if not name:
        return Err(ValidationError("name", "cannot be empty"))
    print(f"Created: {name}")
    return Ok(None)
```

---

## Handle optional parameters

Accept optional CLI parameters and convert them to `Option[T]`.

**Steps:**

1. Declare parameter as `str | None` with default `= None`
2. Import `option_from_optional` from vicepython_core
3. Convert the parameter immediately
4. Pattern match on `Some` / `Nothing`

```python
from vicepython_core import Option, Some, Nothing
from vicepython_core.option import option_from_optional

@app.command_result()
def greet(
    name: str,
    greeting: str | None = None,
) -> Result[None, AppError]:
    greeting_opt: Option[str] = option_from_optional(greeting)

    match greeting_opt:
        case Some(g):
            print(f"{g}, {name}!")
        case Nothing():
            print(f"Hello, {name}!")

    return Ok(None)
```

**Run it:**

```bash
mytool greet Alice                      # Uses default
mytool greet Alice --greeting "Hi"      # Uses "Hi"
```

---

## Test a successful command

Verify that a command returns exit code 0 and produces expected output.

**Steps:**

1. Call `run(app, argv)` with program name as `argv[0]`
2. Assert exit code is 0
3. Use `capsys.readouterr()` to capture output
4. Assert expected output in `captured.out`

```python
from vicepython_ffi_typer import run

def test_greet_success(capsys):
    code = run(app, ["prog", "greet", "Alice"])

    assert code == 0
    captured = capsys.readouterr()
    assert "Hello, Alice!" in captured.out
    assert captured.err == ""
```

---

## Test a failing command

Verify that a command returns exit code 1 and prints an error message to stderr.

**Steps:**

1. Call `run(app, argv)` with arguments that trigger an error
2. Assert exit code is 1
3. Use `capsys.readouterr()` to capture output
4. Assert expected error message in `captured.err`

```python
def test_greet_empty_name(capsys):
    code = run(app, ["prog", "greet", ""])

    assert code == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Name required" in captured.err
```

---

## Build a multi-command app

Create a CLI with multiple commands.

**Steps:**

1. Create one `TypedTyper` instance
2. Decorate multiple functions with `@app.command_result()`
3. Each function becomes a command

```python
from vicepython_ffi_typer import TypedTyper

app = TypedTyper()

@app.command_result()
def create(name: str) -> Result[None, AppError]:
    print(f"Created: {name}")
    return Ok(None)

@app.command_result()
def delete(name: str) -> Result[None, AppError]:
    print(f"Deleted: {name}")
    return Ok(None)

@app.command_result()
def list_all() -> Result[None, AppError]:
    print("Item 1\nItem 2")
    return Ok(None)
```

**Run commands:**

```bash
mytool create myitem
mytool delete myitem
mytool list-all
```

---

## Add help text

Add documentation that appears when users run `--help`.

**Steps for command help:**

1. Pass `help="..."` to `@app.command_result()`

```python
@app.command_result(help="Create a new user account")
def create_user(username: str) -> Result[None, UserError]:
    return Ok(None)
```

**Steps for parameter help:**

1. Import `Annotated`, `Argument`, or `Option`
2. Use `Annotated[type, Argument(help="...")]` or `Annotated[type, Option(help="...")]`

```python
from typing import Annotated
from vicepython_ffi_typer import Argument, Option

@app.command_result()
def process(
    input_file: Annotated[str, Argument(help="Path to input file")],
    verbose: Annotated[bool, Option(help="Enable verbose output")] = False,
) -> Result[None, ProcessError]:
    return Ok(None)
```

**Steps for app-level help:**

1. Pass `help="..."` and `no_args_is_help=True` to `TypedTyper()`

```python
app = TypedTyper(
    help="Task management CLI",
    no_args_is_help=True,
)
```

---

## Use Typer features directly

Use Typer features we don't wrap (prompts, confirmation, progress bars).

**For password input:**

1. Import `typer`
2. Call `typer.prompt()` with `hide_input=True`

```python
import typer

@app.command_result()
def login(username: str) -> Result[None, LoginError]:
    password = typer.prompt("Password", hide_input=True)

    if authenticate(username, password):
        print("Login successful")
        return Ok(None)
    return Err(LoginError("Invalid credentials"))
```

**For confirmation:**

1. Import `typer`
2. Call `typer.confirm()`

```python
import typer

@app.command_result()
def delete(resource: str) -> Result[None, DeleteError]:
    if not typer.confirm(f"Delete {resource}?"):
        print("Cancelled")
        return Ok(None)

    perform_delete(resource)
    print(f"Deleted {resource}")
    return Ok(None)
```

**For progress bars:**

1. Import `rich.progress`
2. Use `track()` or `Progress()` directly

```python
from rich.progress import track

@app.command_result()
def process_batch(count: int) -> Result[None, BatchError]:
    for i in track(range(count), description="Processing"):
        process_item(i)
    return Ok(None)
```

---

## Handle file path arguments

Accept and validate file paths.

**Steps:**

1. Declare parameter as `str`
2. Convert to `Path` inside the handler
3. Check if file exists, is a file, etc.
4. Return `Err()` if validation fails

```python
from pathlib import Path

@app.command_result()
def process_file(path: str) -> Result[None, FileError]:
    file_path = Path(path)

    if not file_path.exists():
        return Err(FileError(f"File not found: {path}"))

    if not file_path.is_file():
        return Err(FileError(f"Not a file: {path}"))

    # Process file
    data = file_path.read_text()
    print(data)
    return Ok(None)
```

---

## Use boolean flags

Add boolean flags that default to False.

**Steps:**

1. Declare parameter as `bool` with default `= False`
2. Use the value in your logic

```python
@app.command_result()
def build(
    release: bool = False,
) -> Result[None, BuildError]:
    mode = "release" if release else "debug"
    print(f"Building in {mode} mode")
    return Ok(None)
```

**Run it:**

```bash
mytool build              # release=False
mytool build --release    # release=True
mytool build --no-release # release=False (explicit)
```

---

## Exit with a specific code

Exit early with a custom exit code (use sparingly).

**Steps:**

1. Import `Exit` from `vicepython_ffi_typer`
2. Raise `Exit(code)` when you need to exit

```python
from vicepython_ffi_typer import Exit

@app.command_result()
def dangerous() -> Result[None, OpError]:
    if not user_confirmed():
        raise Exit(130)  # 128 + SIGINT convention

    perform_operation()
    return Ok(None)
```

**Note:** Prefer `return Err(e)` for normal error handling. Use `Exit` only for framework-level concerns.

---

## Need more context?

For understanding *why* these patterns work, see [Core Concepts](./CONCEPTS.md).

For complete API details, see [API Reference](./API_REFERENCE.md).
