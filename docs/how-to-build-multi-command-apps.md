---
tags: [how-to]
---

# How to build multi-command apps

Create CLIs with multiple commands.

## Problem

Need one CLI with multiple subcommands (like `git commit`, `git push`).

## Solution

Register multiple functions with one `TypedTyper` instance:

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

## Usage

```bash
mytool create myitem
mytool delete myitem
mytool list-all
```

## Key points

- Function names become command names (underscores→hyphens)
- Each command has independent parameters and error types
- All commands share the same app instance

## See also

- [How to require explicit subcommands](./how-to-require-subcommands.md)
- [How to add help text](./how-to-add-help-text.md)
