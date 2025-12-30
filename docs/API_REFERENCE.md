# API Reference

Complete technical specifications for vicepython-ffi-typer's public API.

## Module: `vicepython_ffi_typer`

Package version: 0.1.0

### Public Exports

We expose exactly five names:

| Name | Type | Purpose |
|------|------|---------|
| `TypedTyper` | class | CLI application builder |
| `run` | function | Execute CLI with argv |
| `Argument` | function | Define required arguments |
| `Option` | function | Define optional parameters |
| `Exit` | exception | Framework exit with code |

---

## Class: `TypedTyper`

CLI application builder with typed command registration.

**Constructor:**

```python
TypedTyper(
    *,
    help: str = "",
    no_args_is_help: bool = False,
    require_subcommand: bool = False,
) -> TypedTyper
```

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `help` | `str` | `""` | Application help text shown with `--help` |
| `no_args_is_help` | `bool` | `False` | Show help when invoked without arguments |
| `require_subcommand` | `bool` | `False` | Force group behavior for single-command apps. When `True`, forces `no_args_is_help=True` and registers internal callback to ensure subcommand-first invocation semantics |

**Example:**

```python
from vicepython_ffi_typer import TypedTyper

app = TypedTyper(
    help="Task management CLI",
    no_args_is_help=True,
)
```

### Method: `command_result`

Decorator for commands returning `Result[None, E]`.

**Signature:**

```python
def command_result(
    self,
    name: str | None = None,
    *,
    help: str | None = None,
) -> Callable[[Callable[P, Result[None, E]]], Callable[P, Result[None, E]]]
```

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `name` | `str \| None` | `None` | Command name (defaults to function name with underscores→hyphens) |
| `help` | `str \| None` | `None` | Command help text |

**Returns:** Decorator that preserves original function signature

**Contract:**

Your decorated function must:
- Return `Result[None, E]`
- Return `Ok(None)` on success (not `Ok(any_other_value)`)
- Implement `__str__()` on error type `E` with user-facing messages
- NOT call `sys.exit()` or print errors
- MAY print success output

We enforce these at runtime with `TypeError` for violations.

**Behavior:**

The decorator returns your original function unchanged (registration only). We register a wrapper with Typer internally, but you never see it. The wrapper converts `Err(e)` to an internal exception that `run()` catches.

**Example:**

```python
from dataclasses import dataclass
from vicepython_core import Ok, Err, Result

@dataclass(frozen=True)
class GreetError:
    message: str
    def __str__(self) -> str:
        return self.message

@app.command_result()
def greet(name: str) -> Result[None, GreetError]:
    if not name:
        return Err(GreetError("Name required"))
    print(f"Hello, {name}!")
    return Ok(None)

@app.command_result(
    name="goodbye",
    help="Say goodbye to someone",
)
def farewell(name: str) -> Result[None, GreetError]:
    print(f"Goodbye, {name}!")
    return Ok(None)
```

**Testing:**

Test via `run()`, not direct function calls:

```python
code = run(app, ["prog", "greet", "Alice"])
assert code == 0
```

### Method: `command`

Decorator for commands not using Result semantics.

**Signature:**

```python
def command(
    self,
    name: str | None = None,
    *,
    help: str | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]
```

**Parameters:** Same as `command_result`

**Use Cases:**

- Simple commands without error handling
- Version or help commands
- Commands delegating to Typer's exception handling

**Example:**

```python
from vicepython_ffi_typer import Exit

@app.command()
def version() -> None:
    """Show version information."""
    print("myapp v1.0.0")
    raise Exit(0)
```

We recommend `command_result()` for commands needing error handling.

### Method: `callback`

Decorator for application callbacks.

**Signature:**

```python
def callback(
    self,
    *,
    invoke_without_command: bool = False,
) -> Callable[[Callable[P, R]], Callable[P, R]]
```

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `invoke_without_command` | `bool` | `False` | Execute callback even when no command provided |

**Use Cases:**

- Global options (e.g., `--verbose`, `--config`)
- Initialization logic before command execution
- Validation of global state

**Example:**

```python
@app.callback()
def main(verbose: bool = False) -> None:
    """Configure global settings."""
    if verbose:
        enable_debug_logging()
```

---

## Function: `run`

Execute CLI application with explicit argv.

**Signature:**

```python
def run(app: TypedTyper, argv: list[str]) -> int
```

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `app` | `TypedTyper` | Application instance with registered commands |
| `argv` | `list[str]` | Command-line arguments in `sys.argv` format (MUST include argv[0] as program name) |

**Returns:** Exit code (0-255)

**Raises:**

- `ValueError`: If `argv` is empty

**Exit Codes:**

| Code | Meaning | Cause |
|------|---------|-------|
| 0 | Success | Command returned `Ok(None)` |
| 1 | Domain error | Command returned `Err(e)` |
| 2 | Programmer error | Unexpected exception or `sys.exit()` called |
| N | Framework exit | `raise Exit(N)` from Typer or command |

**Error Handling:**

We print `str(error)` to stderr for domain errors (exit 1), generic messages for programmer errors (exit 2), and no stack traces.

**Non-Reentrant:**

`run()` mutates `sys.argv` temporarily. Don't call `run()` concurrently or nested.

**Example:**

```python
import sys
from vicepython_ffi_typer import TypedTyper, run

app = TypedTyper()

# ... register commands ...

if __name__ == "__main__":
    sys.exit(run(app, sys.argv))
```

**Testing:**

```python
def test_command_success():
    code = run(app, ["prog", "cmd", "arg"])
    assert code == 0

def test_command_error(capsys):
    code = run(app, ["prog", "cmd", "invalid"])
    assert code == 1
    assert "Error message" in capsys.readouterr().err
```

---

## Function: `Argument`

Define required positional arguments with type-safe annotations.

**Signature:**

```python
def Argument(
    *,
    default: Any = ...,
    help: str = "",
) -> Any
```

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `default` | `Any` | `...` (required) | Default value (use `...` for required) |
| `help` | `str` | `""` | Help text for this argument |

**Returns:** Typer sentinel object (use in `Annotated` context only)

**Usage:**

```python
from typing import Annotated
from vicepython_ffi_typer import Argument

@app.command_result()
def process(
    input_file: Annotated[str, Argument(help="Input file path")],
    output_file: Annotated[str, Argument(help="Output file path", default="out.txt")],
) -> Result[None, ProcessError]:
    # Implementation
    return Ok(None)
```

**Command Line:**

```bash
mytool process input.txt            # Uses default output
mytool process input.txt custom.txt # Uses custom output
```

---

## Function: `Option`

Define optional parameters with type-safe annotations.

**Signature:**

```python
def Option(
    *,
    help: str = "",
) -> Any
```

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `help` | `str` | `""` | Help text for this option |

**Returns:** Typer sentinel object (use in `Annotated` context only)

**Usage:**

```python
from typing import Annotated
from vicepython_ffi_typer import Option

@app.command_result()
def query(
    search: str,
    limit: Annotated[int, Option(help="Maximum results")] = 10,
) -> Result[None, QueryError]:
    # Implementation
    return Ok(None)
```

**Command Line:**

```bash
mytool query "python" --limit 50
```

**Optional Parameters:**

For `str | None` types, use VicePython's `Option[T]`:

```python
from vicepython_core import Option as VPOption
from vicepython_core.option import option_from_optional

@app.command_result()
def greet(
    name: str,
    greeting: Annotated[str | None, Option(help="Custom greeting")] = None,
) -> Result[None, GreetError]:
    greeting_opt: VPOption[str] = option_from_optional(greeting)
    # Use pattern matching on greeting_opt
    return Ok(None)
```

---

## Exception: `Exit`

Signal framework exit with specific code.

**Type:** Re-exported from `typer.Exit`

**Signature:**

```python
class Exit(RuntimeError):
    def __init__(self, code: int = 0) -> None: ...
```

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `code` | `int` | 0 | Exit code (0-255) |

**Usage:**

Rare in command handlers; prefer `Err(e)` for domain errors.

```python
from vicepython_ffi_typer import Exit

@app.command_result()
def dangerous() -> Result[None, OpError]:
    if not confirm_action():
        raise Exit(130)  # User cancelled (128 + SIGINT)

    perform_operation()
    return Ok(None)
```

Typer raises `Exit(0)` for `--help` automatically.

---

## Type Requirements

### Error Type Contract

Error types in `Result[None, E]` must:

1. Implement `__str__() -> str` with user-facing messages
2. Produce messages suitable for CLI users (not programmers)
3. Avoid technical jargon, stack traces, or type names

**Recommended Pattern:**

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class MyError:
    """User-facing error for my command."""
    field: str
    reason: str

    def __str__(self) -> str:
        return f"{self.field}: {self.reason}"
```

### Command Handler Contract

Functions decorated with `@app.command_result()` must:

1. Return `Result[None, E]` (not `Result[T, E]` for non-None T)
2. Return `Ok(None)` on success
3. Return `Err(e)` for domain errors
4. NOT call `sys.exit()` (we treat this as a bug)
5. NOT print error messages (only `run()` prints errors)
6. MAY print success output

---

## Not Exported

These are internal implementation details and NOT part of the public API:

- `_CommandError` exception
- `_internal` module
- `TypedTyper._app` attribute (private)
- Typer itself (quarantined)

---

## Version Compatibility

| Component | Version Requirement |
|-----------|-------------------|
| Python | ≥3.12 |
| vicepython-core | ≥0.2.0 |
| typer | ≥0.9.0 |

---

## Design Constraints

We keep this API minimal by design:

- We don't feature-match Typer
- We don't expose every Typer concept
- We don't provide validation frameworks
- We don't wrap convenience utilities

For features we don't wrap, import `typer` directly:

```python
import typer

password = typer.prompt("Password", hide_input=True)
confirmed = typer.confirm("Continue?")
```

---

## Related Documentation

- [Getting Started](./GETTING_STARTED.md) — Tutorial
- [User Guide](./USER_GUIDE.md) — Task-focused how-tos
- [Core Concepts](./CONCEPTS.md) — Design rationale
- [Quarantined CLI Boundary Pattern](../quarantining-cli-frameworks.md) — Full pattern documentation
