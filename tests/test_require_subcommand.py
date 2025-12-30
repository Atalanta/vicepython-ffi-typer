"""Tests for require_subcommand parameter in TypedTyper."""

import pytest

from vicepython_ffi_typer import TypedTyper, run


def test_single_command_default_behavior(capsys: pytest.CaptureFixture[str]) -> None:
    """Single-command app with require_subcommand=False executes command directly."""
    app = TypedTyper(require_subcommand=False)

    @app.command()
    def doctor() -> None:
        """Run diagnostic checks."""
        print("the doctor is in the house")

    exit_code = run(app, ["prog"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.out == "the doctor is in the house\n"


def test_single_command_forced_group_no_args(capsys: pytest.CaptureFixture[str]) -> None:
    """Single-command app with require_subcommand=True shows help when no args."""
    app = TypedTyper(require_subcommand=True)

    @app.command()
    def doctor() -> None:
        """Run diagnostic checks."""
        print("the doctor is in the house")

    exit_code = run(app, ["prog"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Usage:" in captured.out
    assert "doctor" in captured.out


def test_single_command_forced_group_with_command(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Single-command app with require_subcommand=True executes when command given."""
    app = TypedTyper(require_subcommand=True)

    @app.command()
    def doctor() -> None:
        """Run diagnostic checks."""
        print("the doctor is in the house")

    exit_code = run(app, ["prog", "doctor"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.out == "the doctor is in the house\n"


def test_multi_command_app_no_args(capsys: pytest.CaptureFixture[str]) -> None:
    """Multi-command app shows help when no command given (with no_args_is_help)."""
    app = TypedTyper(no_args_is_help=True)

    @app.command()
    def doctor() -> None:
        """Run diagnostic checks."""
        print("the doctor is in the house")

    @app.command()
    def status() -> None:
        """Show status."""
        print("status ok")

    exit_code = run(app, ["prog"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Usage:" in captured.out
    assert "doctor" in captured.out
    assert "status" in captured.out


def test_multi_command_app_with_command(capsys: pytest.CaptureFixture[str]) -> None:
    """Multi-command app executes the specified command."""
    app = TypedTyper()

    @app.command()
    def doctor() -> None:
        """Run diagnostic checks."""
        print("the doctor is in the house")

    @app.command()
    def status() -> None:
        """Show status."""
        print("status ok")

    exit_code = run(app, ["prog", "doctor"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.out == "the doctor is in the house\n"
