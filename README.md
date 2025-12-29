# vicepython-ffi-typer

A typed CLI framework wrapper that enforces Result semantics at the boundary. We quarantine Typer's type system behind a clean VicePython interface.

## Installation

```bash
uv add vicepython-ffi-typer
```

Requires Python ≥3.12 and vicepython-core.

## Quick Start

```python
from vicepython_core import Ok, Err, Result
from vicepython_ffi_typer import TypedTyper, run
import sys

app = TypedTyper()

@app.command_result()
def greet(name: str) -> Result[None, str]:
    if not name:
        return Err("Name can't be empty")
    print(f"Hello, {name}!")
    return Ok(None)

if __name__ == "__main__":
    sys.exit(run(app, sys.argv))
```

## Documentation

**New to this library?** Start with the tutorial.

**Building something specific?** Jump to the task-focused guides.

**Need technical details?** Check the reference.

**Want to understand why?** Read the concepts.

### Tutorial (Learning-Oriented)

**[Getting Started](./docs/GETTING_STARTED.md)** — Build your first CLI in 15 minutes

### How-To Guides (Task-Oriented)

**[User Guide](./docs/USER_GUIDE.md)** — Solve specific problems:
- Create error types
- Handle optional parameters
- Test commands
- Build multi-command apps
- Use Typer features directly

### Reference (Information-Oriented)

**[API Reference](./docs/API_REFERENCE.md)** — Complete technical specifications

### Explanation (Understanding-Oriented)

**[Core Concepts](./docs/CONCEPTS.md)** — Understand error handling, exit codes, and testing philosophy

**[Quarantined CLI Boundary Pattern](./quarantining-cli-frameworks.md)** — Why this library exists

## Contributing

Run checks before submitting:

```bash
uv run mypy --strict src/ tests/
uv run pytest
```

We maintain a minimal API surface by design.
