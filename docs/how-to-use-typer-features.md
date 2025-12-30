---
tags: [how-to]
---

# How to use Typer features directly

Use Typer features we don't wrap (prompts, confirmation, progress bars).

## Problem

Need features like password input or confirmation dialogs not wrapped by vicepython-ffi-typer.

## Solution

Import `typer` and use its features directly within commands.

### Password input

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

### Confirmation

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

### Progress bars

```python
from rich.progress import track

@app.command_result()
def process_batch(count: int) -> Result[None, BatchError]:
    for i in track(range(count), description="Processing"):
        process_item(i)
    return Ok(None)
```

## Key points

- Import `typer` or `rich` directly for unwrapped features
- Use inside command handlers, not at module level
- These features don't affect `Result` semantics

## See also

- [Typer documentation](https://typer.tiangolo.com/)
- [Rich documentation](https://rich.readthedocs.io/)
