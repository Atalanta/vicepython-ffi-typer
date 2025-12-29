"""Tests for command_result decorator behavior.

These tests verify the decorator contract by invoking commands through run(),
not by calling decorated functions directly. The decorator is for Typer
registration, and behavior is tested at the CLI boundary.
"""

from dataclasses import dataclass

import pytest
from vicepython_core import Err, Ok, Result

from vicepython_ffi_typer import TypedTyper, run


@dataclass(frozen=True)
class CommandError:
    message: str

    def __str__(self) -> str:
        return self.message


def test_ok_via_run(capsys: pytest.CaptureFixture[str]) -> None:
    """Ok(None) should result in exit code 0."""
    app = TypedTyper()

    @app.command_result()
    def succeeds() -> Result[None, CommandError]:
        return Ok(None)

    code = run(app, ["prog"])

    assert code == 0
    captured = capsys.readouterr()
    assert captured.err == ""


def test_err_via_run(capsys: pytest.CaptureFixture[str]) -> None:
    """Err(e) should result in exit code 1 with error message."""
    app = TypedTyper()

    @app.command_result()
    def fails() -> Result[None, CommandError]:
        return Err(CommandError("something broke"))

    code = run(app, ["prog"])

    assert code == 1
    captured = capsys.readouterr()
    assert "something broke" in captured.err


def test_decorator_preserves_signature() -> None:
    """Decorated function should preserve original signature for type checking."""
    app = TypedTyper()

    @app.command_result()
    def my_command(name: str, count: int) -> Result[None, CommandError]:
        return Ok(None)

    # Type checker should see original signature
    # This is a compile-time test - if it type-checks, it passes
    result: Result[None, CommandError] = my_command("test", 42)
    assert result == Ok(None)
