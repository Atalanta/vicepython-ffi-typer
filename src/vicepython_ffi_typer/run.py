"""CLI run boundary - the only place that prints errors and returns exit codes.

This module implements the Quarantined CLI Boundary pattern.
All error I/O and exit code decisions happen here. Command handlers may print
success output directly, but MUST NOT print error messages or call sys.exit().

Contract (Posture A - Strict VicePython):
- Command handlers MUST NOT call sys.exit() - this is treated as a bug
- run() uses standalone_mode=False to prevent Typer from calling sys.exit()
- Only Typer's Exit exception (from --help, etc.) is respected
- ALL SystemExit instances are treated as bugs (exit code 2)
- No carve-outs for SystemExit(0) - if you see it, it's a handler bug
"""

import sys

from ._internal import _CommandError
from .typed_typer import Exit, TypedTyper


def _exit_code_from_exit(e: Exit) -> int:
    """Extract exit code from Typer Exit exception.

    Typer's Exit may use .exit_code or .code depending on version.
    This helper provides a single extraction point.
    """
    if hasattr(e, "exit_code"):
        code = e.exit_code
        return code if isinstance(code, int) else 0
    if hasattr(e, "code"):
        code = e.code
        return code if isinstance(code, int) else 0
    return 0


def run(app: TypedTyper, argv: list[str]) -> int:
    """Execute CLI app with explicit argv. Returns exit code.

    This is the ONLY function that prints error messages and the ONLY function
    that determines exit codes. Command handlers may print success output but
    MUST NOT print errors or call sys.exit - they return Result[None, E] instead.

    Exit Code Semantics:
        0: Command handler returned Ok(None)
        1: Command handler returned Err(e) - prints str(e) to stderr
        2: Unexpected exception or ANY SystemExit - prints generic bug message to stderr
        N: typer.Exit(N) was raised by framework (e.g., --help) - returns N

    Contract (Strict - Posture A):
        - Command handlers calling sys.exit() is a BUG (treated as exit 2)
        - ALL SystemExit instances are bugs - no exceptions
        - Only Typer's Exit (RuntimeError subclass) is respected for exit codes
        - standalone_mode=False prevents Typer from calling sys.exit()

    Args:
        app: TypedTyper instance with registered commands
        argv: Command-line arguments in sys.argv format. MUST include argv[0]
              as the program name (e.g., ["prog", "greet", "Alice"]).
              This mirrors sys.argv semantics and avoids Click parsing issues.

    Returns:
        Exit code (0 for success, non-zero for errors)

    Raises:
        ValueError: If argv is empty (missing program name)

    Example:
        app = TypedTyper()

        @app.command_result()
        def greet(name: str) -> Result[None, GreetError]:
            if not name:
                return Err(GreetError("Name required"))
            print(f"Hello, {name}!")
            return Ok(None)

        # In tests (note argv[0] = "prog"):
        code = run(app, ["prog", "greet", "Alice"])
        assert code == 0

        # In __main__.py:
        sys.exit(run(app, sys.argv))
    """
    if not argv:
        raise ValueError("argv must not be empty - argv[0] should be program name")

    # Mutates process global state; not re-entrant but acceptable at CLI boundary
    old_argv = sys.argv
    try:
        sys.argv = argv
        app._app(standalone_mode=False)
        return 0
    except _CommandError as e:
        print(str(e.error), file=sys.stderr)
        return 1
    except Exit as e:
        return _exit_code_from_exit(e)
    except SystemExit:
        print("Unexpected error (bug): SystemExit", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Unexpected error (bug): {type(e).__name__}", file=sys.stderr)
        return 2
    finally:
        sys.argv = old_argv
