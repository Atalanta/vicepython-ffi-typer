---
tags: [how-to]
---

# How to exit with custom exit codes

Exit early with non-standard exit codes (use sparingly).

## Problem

Need to exit with specific codes for signal conventions or special cases.

## Solution

Import `Exit` and raise with desired code:

```python
from vicepython_ffi_typer import Exit

@app.command_result()
def dangerous() -> Result[None, OpError]:
    if not user_confirmed():
        raise Exit(130)  # 128 + SIGINT convention

    perform_operation()
    return Ok(None)
```

## Standard exit codes

- 0: Success
- 1: Command error (via `Err(e)`)
- 2: Programming error (unexpected exception)
- 130: User cancelled (128 + SIGINT)

## When to use

- Signal conventions (130 for Ctrl-C simulation)
- Tool-specific protocols requiring specific codes
- Framework-level exit needs

**Prefer `return Err(e)` for normal errors** - it returns exit code 1 and prints error message.

## See also

- [API Reference: Exit exception](./API_REFERENCE.md#exit)
- [Concepts: Exit code semantics](./CONCEPTS.md)
