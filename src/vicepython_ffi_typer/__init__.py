"""VicePython FFI Typer - Typed CLI framework façade with Result semantics.

This package quarantines Typer at the boundary and provides a clean,
typed interface for building CLIs with explicit error handling.

Public API (minimal by design):
    TypedTyper: App builder with command_result decorator
    run: Execute app with argv, returns exit code
    Argument, Option: Basic type-safe parameter helpers
    Exit: Exception for explicit exit codes (re-exported from typer)
"""

from .run import run
from .typed_typer import Argument, Exit, Option, TypedTyper

__all__ = [
    # Core API
    "TypedTyper",
    "run",
    # Parameter helpers
    "Argument",
    "Option",
    # Framework integration
    "Exit",
]

__version__ = "0.1.0"
