---
tags: [how-to]
---

# How to add help text

Add documentation shown with `--help`.

## Problem

Users need to understand what commands and parameters do.

## Solution

Add help at three levels: command, parameter, and app.

### Command help

```python
@app.command_result(help="Create a new user account")
def create_user(username: str) -> Result[None, UserError]:
    return Ok(None)
```

### Parameter help

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

### App-level help

```python
app = TypedTyper(
    help="Task management CLI",
    no_args_is_help=True,
)
```

## Key points

- Command help: use `help=` parameter in decorator
- Parameter help: use `Annotated` with `Argument()` or `Option()`
- App help: use `help=` in `TypedTyper()` constructor
- Set `no_args_is_help=True` to show help when invoked without args

## See also

- [API Reference: TypedTyper parameters](./API_REFERENCE.md#class-typedtyper)
- [API Reference: Argument and Option](./API_REFERENCE.md#function-argument)
