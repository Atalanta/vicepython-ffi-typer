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

Core tasks:
- **[Create error types](./docs/how-to-create-error-types.md)** — Define typed errors with user-facing messages
- **[Build multi-command apps](./docs/how-to-build-multi-command-apps.md)** — Create CLIs with multiple subcommands
- **[Test successful commands](./docs/how-to-test-successful-commands.md)** — Verify exit codes and output
- **[Test failing commands](./docs/how-to-test-failing-commands.md)** — Verify error handling

Parameters and options:
- **[Handle optional parameters](./docs/how-to-handle-optional-parameters.md)** — Convert `None` to `Option[T]`
- **[Use boolean flags](./docs/how-to-use-boolean-flags.md)** — Add `--flag` options
- **[Handle file paths](./docs/how-to-handle-file-paths.md)** — Accept and validate paths
- **[Add help text](./docs/how-to-add-help-text.md)** — Document commands and parameters

Advanced:
- **[Require explicit subcommands](./docs/how-to-require-subcommands.md)** — Force group behavior for single-command apps
- **[Use Typer features directly](./docs/how-to-use-typer-features.md)** — Prompts, confirmation, progress bars
- **[Exit with custom codes](./docs/how-to-exit-with-custom-codes.md)** — Non-standard exit codes

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
