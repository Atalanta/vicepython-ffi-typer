"""Tests for run() boundary - exit codes and printing."""

from dataclasses import dataclass

import pytest
from vicepython_core import Err, Ok, Result

from vicepython_ffi_typer import Exit, TypedTyper, run


@dataclass(frozen=True)
class CliError:
    message: str

    def __str__(self) -> str:
        return self.message


def test_ok_returns_zero(capsys: pytest.CaptureFixture[str]) -> None:
    """Ok(None) should return exit code 0 with no output."""
    app = TypedTyper()

    @app.command_result()
    def success() -> Result[None, CliError]:
        return Ok(None)

    code = run(app, ["prog"])

    assert code == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_err_returns_one_prints_error(capsys: pytest.CaptureFixture[str]) -> None:
    """Err(e) should return exit code 1 and print str(e) to stderr."""
    app = TypedTyper()

    @app.command_result()
    def fails() -> Result[None, CliError]:
        return Err(CliError("operation failed"))

    code = run(app, ["prog"])

    assert code == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "operation failed\n"


def test_exception_returns_two_prints_generic(capsys: pytest.CaptureFixture[str]) -> None:
    """Unexpected exception should return exit code 2 with generic message."""
    app = TypedTyper()

    @app.command_result()
    def crashes() -> Result[None, CliError]:
        raise ValueError("unexpected bug")

    code = run(app, ["prog"])

    assert code == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Unexpected error (bug): ValueError" in captured.err


def test_argv_injection_works() -> None:
    """run() should use provided argv, not sys.argv."""
    app = TypedTyper()
    received_name: str | None = None

    @app.command_result()
    def greet(name: str) -> Result[None, CliError]:
        nonlocal received_name
        received_name = name
        return Ok(None)

    code = run(app, ["prog", "Alice"])

    assert code == 0
    assert received_name == "Alice"


def test_empty_argv_raises() -> None:
    """run() should raise ValueError if argv is empty."""
    app = TypedTyper()

    @app.command_result()
    def dummy() -> Result[None, CliError]:
        return Ok(None)

    with pytest.raises(ValueError, match="argv must not be empty"):
        run(app, [])


def test_systemexit_treated_as_bug(capsys: pytest.CaptureFixture[str]) -> None:
    """Handler calling sys.exit() should be treated as a bug (exit 2)."""
    app = TypedTyper()

    @app.command_result()
    def bad_handler() -> Result[None, CliError]:
        import sys

        sys.exit(42)

    code = run(app, ["prog"])

    assert code == 2
    captured = capsys.readouterr()
    assert "Unexpected error (bug): SystemExit" in captured.err


def test_help_flag_exits_cleanly(capsys: pytest.CaptureFixture[str]) -> None:
    """--help should exit cleanly via Typer's Exit (not treated as bug)."""
    app = TypedTyper(help="Test app")

    @app.command_result()
    def my_command() -> Result[None, CliError]:
        return Ok(None)

    code = run(app, ["prog", "--help"])

    assert code == 0
    captured = capsys.readouterr()
    assert "--help" in captured.out
    assert "bug" not in captured.err.lower()
