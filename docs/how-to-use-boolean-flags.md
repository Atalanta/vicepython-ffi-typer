---
tags: [how-to]
---

# How to use boolean flags

Add boolean flags that default to False.

## Problem

Need on/off flags like `--verbose` or `--release`.

## Solution

Declare parameter as `bool = False`:

```python
@app.command_result()
def build(
    release: bool = False,
) -> Result[None, BuildError]:
    mode = "release" if release else "debug"
    print(f"Building in {mode} mode")
    return Ok(None)
```

## Usage

```bash
mytool build              # release=False
mytool build --release    # release=True
mytool build --no-release # release=False (explicit)
```

## Key points

- Typer automatically creates `--flag` and `--no-flag` variants
- Default value becomes the flag's default behavior
- Use descriptive parameter names (they become CLI flags)

## See also

- [How to add help text](./how-to-add-help-text.md)
