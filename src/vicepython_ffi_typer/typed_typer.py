"""Fully-typed façade over Typer with no Any leakage to calling code.

This module quarantines Typer's type pollution behind a clean interface.
The Option/Argument functions return Any because they return Typer's internal
sentinel objects, but they're only used in Annotated contexts where the actual
type is declared separately (e.g., Annotated[str, Option(...)]).

This is the quarantine boundary - Any stays here, concrete types flow to callers.
"""

import functools
from typing import Annotated, Any, Callable, ParamSpec, TypeVar

import typer as _typer
from vicepython_core import Err, Ok, Result

from ._internal import _CommandError

Exit = _typer.Exit

P = ParamSpec("P")
R = TypeVar("R")
E = TypeVar("E")


class TypedTyper:
    """Typed wrapper around Typer app with clean generic decorators."""

    def __init__(
        self,
        *,
        help: str = "",
        no_args_is_help: bool = False,
        require_subcommand: bool = False,
    ) -> None:
        """Initialize a TypedTyper app.

        Args:
            help: Help text for the app
            no_args_is_help: Show help when no args provided
            require_subcommand: Force group behavior even for single-command apps.
                When True, no_args_is_help is forced to True, and an internal
                callback is registered to ensure the app behaves like a group
                (requiring explicit subcommand invocation).
        """
        self._require_subcommand = require_subcommand
        effective_no_args_is_help = require_subcommand or no_args_is_help

        self._app: Any = _typer.Typer(
            help=help,
            no_args_is_help=effective_no_args_is_help,
        )

        if self._require_subcommand:
            @self._app.callback()
            def _vp_internal_callback() -> None:
                """Internal callback to force group behavior. Do not use directly."""
                pass

    def command(
        self,
        name: str | None = None,
        *,
        help: str | None = None,
    ) -> Callable[[Callable[P, R]], Callable[P, R]]:
        """Decorator for commands that don't use Result semantics.

        Use this for simple commands that don't need error handling
        (e.g., --version, --completion).

        Prefer command_result() for commands that need explicit error handling.
        """

        def decorator(func: Callable[P, R]) -> Callable[P, R]:
            _ = self._app.command(name=name, help=help)(func)
            return func

        return decorator

    def callback(
        self,
        *,
        invoke_without_command: bool = False,
    ) -> Callable[[Callable[P, R]], Callable[P, R]]:
        """Decorator for app callbacks that don't use Result semantics.

        Use this for simple callbacks that don't need error handling.

        Prefer command_result() for commands that need explicit error handling.
        """

        def decorator(func: Callable[P, R]) -> Callable[P, R]:
            _ = self._app.callback(invoke_without_command=invoke_without_command)(func)
            return func

        return decorator

    def command_result(
        self,
        name: str | None = None,
        *,
        help: str | None = None,
    ) -> Callable[[Callable[P, Result[None, E]]], Callable[P, Result[None, E]]]:
        """Decorator for commands that return Result[None, E].

        This decorator is for Typer registration only. The returned function
        preserves the original signature but is wrapped internally for CLI use.

        Contract:
        - Handler MUST return Result[None, E] where success value is ONLY Ok(None)
        - Handler MUST NOT call sys.exit() - this is treated as a bug
        - Returning Ok(any_other_value) is a programmer error (runtime TypeError)
        - E MUST have __str__ that produces human-readable error messages
        - Wrapper catches Err(e) and raises _CommandError for run() to handle
        - Decorator returns original function (wrapper is internal to Typer)

        The decorated function is meant to be invoked via run(app, argv), not
        called directly. Test the CLI behavior through run(), not direct calls.

        Only run() prints errors and determines exit codes.

        Example:
            @app.command_result()
            def my_command(name: str) -> Result[None, MyError]:
                if not name:
                    return Err(MyError("Name cannot be empty"))
                process_name(name)
                return Ok(None)

            # Test via run(), not direct calls:
            code = run(app, ["prog", "my-command", "value"])
            assert code == 0
        """

        def decorator(func: Callable[P, Result[None, E]]) -> Callable[P, Result[None, E]]:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                result = func(*args, **kwargs)
                match result:
                    case Ok(None):
                        return result
                    case Err(e):
                        raise _CommandError(error=e)
                    case Ok(value):
                        # Programmer error: Ok(non-None) is invalid
                        raise TypeError(
                            f"command_result handler must return Ok(None), "
                            f"got Ok({value!r})"
                        )
                    case _:
                        # Type system should prevent this, but fail loudly if violated
                        raise TypeError(
                            f"command_result handler must return Result[None, E], "
                            f"got {type(result)}"
                        )

            # Register wrapper with Typer (pollutes with Any, we ignore)
            _ = self._app.command(name=name, help=help)(wrapper)

            # Return original function - decorator is for registration only
            # The wrapper is internal to Typer, not exposed to callers
            return func

        return decorator

    def __call__(self) -> None:
        """Run the Typer app."""
        self._app()


def Argument(  # noqa: N802
    *,
    default: Any = ...,
    help: str = "",
) -> Any:
    """Typed wrapper for Argument.

    Returns Any because it's a Typer sentinel object, but safe because
    only used in Annotated[T, Argument(...)] where T provides the actual type.
    """
    return _typer.Argument(default=default, help=help)


def Option(  # noqa: N802
    *,
    help: str = "",
) -> Any:
    """Typed wrapper for Option.

    Returns Any because it's a Typer sentinel object, but safe because
    only used in Annotated[T, Option(...)] where T provides the actual type.

    No default parameter - Typer infers it from the function parameter default value.
    """
    return _typer.Option(help=help)
