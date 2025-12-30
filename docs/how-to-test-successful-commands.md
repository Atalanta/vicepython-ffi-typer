---
tags: [how-to]
---

# How to test successful commands

Verify commands return exit code 0 and produce expected output.

## Problem

Need to test command success without subprocess overhead.

## Solution

Use `run()` with `capsys` fixture:

```python
from vicepython_ffi_typer import run
import pytest

def test_greet_success(capsys: pytest.CaptureFixture[str]) -> None:
    code = run(app, ["prog", "greet", "Alice"])

    assert code == 0
    captured = capsys.readouterr()
    assert "Hello, Alice!" in captured.out
    assert captured.err == ""
```

## Key points

- `argv[0]` must be program name (e.g., `"prog"`)
- Exit code 0 indicates success
- Success output appears in `stdout`
- `stderr` should be empty on success
- Use `capsys.readouterr()` to capture output

## See also

- [API Reference: run function](./API_REFERENCE.md#function-run)
- [How to test failing commands](./how-to-test-failing-commands.md)
