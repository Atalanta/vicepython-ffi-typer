---
tags: [how-to]
---

# How to handle file paths

Accept and validate file path arguments.

## Problem

Commands need to accept file paths and validate they exist.

## Solution

Accept as `str`, convert to `Path`, validate:

```python
from pathlib import Path

@app.command_result()
def process_file(path: str) -> Result[None, FileError]:
    file_path = Path(path)

    if not file_path.exists():
        return Err(FileError(f"File not found: {path}"))

    if not file_path.is_file():
        return Err(FileError(f"Not a file: {path}"))

    data = file_path.read_text()
    print(data)
    return Ok(None)
```

## Pattern

1. Accept `str` parameter (Typer handles CLI input)
2. Convert to `Path` inside handler
3. Validate existence, type, permissions
4. Return `Err()` for validation failures
5. Perform file operations

## Why not accept `Path` directly?

Typer supports `Path` parameters, but explicit conversion keeps validation logic visible and testable.

## See also

- [How to create error types](./how-to-create-error-types.md)
- [Python pathlib documentation](https://docs.python.org/3/library/pathlib.html)
