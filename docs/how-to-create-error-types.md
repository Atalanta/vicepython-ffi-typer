---
tags: [how-to]
---

# How to create error types

Define error types for your command's `Err()` returns.

## Problem

Commands need to return typed errors with user-facing messages.

## Solution

Create a frozen dataclass with `__str__()`:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class ValidationError:
    field: str
    reason: str

    def __str__(self) -> str:
        return f"Invalid {self.field}: {self.reason}"
```

Use it in commands:

```python
@app.command_result()
def create(name: str) -> Result[None, ValidationError]:
    if not name:
        return Err(ValidationError("name", "cannot be empty"))
    print(f"Created: {name}")
    return Ok(None)
```

## Requirements

- Must implement `__str__()` returning user-facing message
- Recommended: use `frozen=True` for immutability
- Message appears in stderr when command returns `Err(e)`

## See also

- [API Reference: command_result contract](./API_REFERENCE.md#method-command_result)
