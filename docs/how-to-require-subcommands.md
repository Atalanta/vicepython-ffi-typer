---
tags: [how-to]
---

# How to require explicit subcommands

Force single-command apps to behave like groups.

## Problem

By default, `mytool` with one command executes immediately. You want `mytool` to show help, requiring users to type `mytool command`.

## Solution

Set `require_subcommand=True`:

```python
from vicepython_ffi_typer import TypedTyper
from vicepython_core import Ok, Result

app = TypedTyper(require_subcommand=True)

@app.command_result()
def doctor() -> Result[None, AppError]:
    print("Running diagnostics...")
    return Ok(None)
```

## Behavior

```bash
mytool          # Shows help, exits 0
mytool doctor   # Runs the command
```

## When to use this

Use `require_subcommand=True` when:

- Building a single-command tool that will grow to multiple commands
- Enforcing consistent invocation patterns across your CLIs
- Preventing accidental execution when users explore with `mytool`

## See also

- [API Reference: TypedTyper constructor](./API_REFERENCE.md#class-typedtyper)
- [How to build multi-command apps](./USER_GUIDE.md#build-a-multi-command-app)
