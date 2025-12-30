---
tags: [how-to]
---

# How to test failing commands

Verify commands return exit code 1 and print error messages to stderr.

## Problem

Need to test error handling without subprocess overhead.

## Solution

Trigger error and check exit code and stderr:

```python
import pytest

def test_greet_empty_name(capsys: pytest.CaptureFixture[str]) -> None:
    code = run(app, ["prog", "greet", ""])

    assert code == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Name required" in captured.err
```

## Key points

- Exit code 1 indicates command returned `Err(e)`
- Error message (from `__str__()`) appears in `stderr`
- `stdout` should be empty on error
- `run()` handles error printing automatically

## See also

- [API Reference: exit code semantics](./API_REFERENCE.md#function-run)
- [How to create error types](./how-to-create-error-types.md)
