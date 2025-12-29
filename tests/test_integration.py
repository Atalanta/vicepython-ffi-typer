"""Integration tests - end-to-end CLI scenarios."""

from dataclasses import dataclass

import pytest
from vicepython_core import Err, Nothing, Ok, Option, Result, Some
from vicepython_core.option import option_from_optional

from vicepython_ffi_typer import TypedTyper, run


@dataclass(frozen=True)
class AppError:
    reason: str

    def __str__(self) -> str:
        return f"Error: {self.reason}"


def test_realistic_cli_with_optional_conversion(capsys: pytest.CaptureFixture[str]) -> None:
    """Realistic example: Optional param converted to Option at boundary."""
    app = TypedTyper()

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

    code = run(app, ["prog", "Alice", "--greeting", "Hi"])
    assert code == 0
    captured = capsys.readouterr()
    assert "Hi, Alice!" in captured.out

    code = run(app, ["prog", "Bob"])
    assert code == 0
    captured = capsys.readouterr()
    assert "Hello, Bob!" in captured.out


def test_multi_command_app(capsys: pytest.CaptureFixture[str]) -> None:
    """App with multiple commands using command_result."""
    app = TypedTyper()

    @app.command_result()
    def add(a: int, b: int) -> Result[None, AppError]:
        print(a + b)
        return Ok(None)

    @app.command_result()
    def sub(a: int, b: int) -> Result[None, AppError]:
        if b == 0:
            return Err(AppError("Cannot subtract zero"))
        print(a - b)
        return Ok(None)

    assert run(app, ["prog", "add", "2", "3"]) == 0
    assert run(app, ["prog", "sub", "5", "3"]) == 0
    assert run(app, ["prog", "sub", "5", "0"]) == 1
