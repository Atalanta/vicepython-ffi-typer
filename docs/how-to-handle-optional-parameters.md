---
tags: [how-to]
---

# How to handle optional parameters

Accept optional CLI parameters and convert them to `Option[T]`.

## Problem

Need to handle parameters that may or may not be provided without using `None` in domain logic.

## Solution

Declare parameter as `str | None = None` and convert immediately:

```python
from vicepython_core import Option, Some, Nothing
from vicepython_core.option import option_from_optional

@app.command_result()
def greet(
    name: str,
    greeting: str | None = None,
) -> Result[None, AppError]:
    greeting_opt: Option[str] = option_from_optional(greeting)

    match greeting_opt:
        case Some(g):
            print(f"{g}, {name}!")
        case Nothing():
            print(f"Hello, {name}!")

    return Ok(None)
```

## Usage

```bash
mytool greet Alice                      # Uses default
mytool greet Alice --greeting "Hi"      # Uses "Hi"
```

## Pattern

1. Accept `T | None = None` at boundary
2. Convert to `Option[T]` immediately
3. Pattern match on `Some` / `Nothing`
4. Keep domain logic free of `None`

## See also

- [VicePython Core: Option documentation](https://github.com/Atalanta/vicepython-core)
