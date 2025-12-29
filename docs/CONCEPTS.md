# Core Concepts

This document explains the design decisions behind vicepython-ffi-typer and why it works the way it does.

## The Quarantine Boundary

We built this library to solve a specific problem: CLI frameworks like Typer use `Optional`, `None`, and exceptions, but VicePython code uses `Option`, `Result`, and explicit error values. When these two worlds meet, you get semantic leakage—framework conventions creep into domain logic.

The solution is quarantine. We wrap Typer at the boundary, translate its semantics, and expose only VicePython types to your code. Your command handlers never import Typer. They don't see its `Any`-polluted types. They work with `Result[None, E]` and nothing else.

This isn't about avoiding Typer—it's about controlling where its conventions stop. See [quarantining-cli-frameworks.md](../quarantining-cli-frameworks.md) for the full pattern.

## Why Result[None, E], Not Result[T, E]

You might expect command handlers to return `Result[T, E]` where `T` is some useful value. We don't allow that. Success is always `Ok(None)`.

Here's why: CLI commands are I/O boundaries. They print output, write files, or send network requests. The "return value" is the side effect, not a value you can compose with other functions.

If you let handlers return `Ok(some_value)`, you create confusion:
- What should we do with that value? Print it? Serialize it? Ignore it?
- Different commands would need different handling logic
- The boundary becomes muddy—is this a function or a CLI command?

By enforcing `Ok(None)`, we're saying: "If your command succeeds, it already did what it needed to do. There's nothing to return." Print your output inside the handler. Write your files. Then return `Ok(None)`.

This constraint keeps the boundary clean.

## Exit Codes as Semantic Categories

We use exit codes to distinguish error *types*, not to encode specific failures:

| Code | Meaning | Example |
|------|---------|---------|
| 0 | Success | `Ok(None)` |
| 1 | Domain error | `Err(ValidationError("Name required"))` |
| 2 | Programmer error | Unexpected exception, `sys.exit()` called |
| N | Framework exit | `raise Exit(N)` (rare) |

**Exit code 1 means "the user did something wrong."** Invalid input, missing file, business rule violation. These are expected failures. Your error message tells them how to fix it.

**Exit code 2 means "the code did something wrong."** Unhandled exception, assertion failure, calling `sys.exit()` in a command handler. These are bugs. We print a generic message to avoid leaking implementation details.

This distinction matters for tooling. Scripts can check `$?` and treat 1 differently from 2. Monitoring systems can alert on exit 2 (bugs) but ignore exit 1 (user errors).

We chose this over encoding specific failures (exit 3 for "file not found", exit 4 for "network error") because:
- You'd run out of codes quickly
- Callers can't know what your specific codes mean
- The error message already contains the details

## Error Types: Frozen Dataclasses With Good __str__

We recommend frozen dataclasses for error types:

```python
@dataclass(frozen=True)
class ValidationError:
    field: str
    reason: str

    def __str__(self) -> str:
        return f"Invalid {self.field}: {self.reason}"
```

Let's break down why:

**Frozen** means immutable. Errors shouldn't change after creation. Immutability prevents bugs where error state gets modified unexpectedly.

**Dataclasses** give you structure without boilerplate. You can carry multiple fields (field, reason, code, path) and access them in tests, but you're not writing constructors and equality methods by hand.

**`__str__` for user-facing messages** separates representation from data. The fields are for programmatic access (tests, logging). The string is for humans. This lets you change the message format without breaking code that inspects the fields.

We don't use exceptions for errors because exceptions are control flow, and we want errors to be values. `Err(e)` is a value you can inspect, match on, and pass around. An exception is something you throw across frames. Values compose better than control flow.

## The Single I/O Point

Only `run()` prints errors and determines exit codes. Command handlers return `Result[None, E]`. They don't print error messages. They don't call `sys.exit()`. They don't decide exit codes.

This separation exists because:

**Testability** — If handlers print errors, you can't test the error logic without capturing stderr. If they call `sys.exit()`, you can't test them without catching SystemExit. By returning `Result`, testing becomes straightforward: call the function, match the result.

**Consistency** — One place owns error formatting. You're not debugging six different print statements scattered across commands. Want to change error format? Update `run()`. Done.

**Composability** — Handlers that return values can be tested independently, mocked, or reused outside the CLI. Handlers that do I/O can't.

This is a hard constraint. We catch `sys.exit()` and treat it as exit code 2 (bug). We don't provide escape hatches. If you need to exit early, return `Err(e)`.

## Why Test Via run(), Not Direct Calls

We require tests to invoke `run(app, argv)`, not call decorated functions directly. Here's why:

The decorator returns your original function unchanged. It registers a *wrapper* with Typer, but that wrapper only runs when you invoke the CLI via `run()`. If you call the decorated function directly, you're testing the unwrapped function—you bypass the entire boundary layer.

This means:
- Exit codes won't work (you'll get `Ok(None)` or `Err(e)`, not exit codes)
- Error printing won't work (nothing prints to stderr)
- Framework behavior won't work (argv parsing, help text, etc.)

You'll write tests that pass but don't verify the CLI contract. When users actually run your tool, it'll behave differently.

By forcing tests through `run()`, we ensure you're testing what users see. The full stack: argv parsing, error translation, exit codes, stderr output. No shortcuts.

## Type System Honesty

We prefer changing our goals over lying to the type checker. You won't find `cast()` or `type: ignore` in this codebase.

Example: We originally wanted decorators that wrap functions and preserve signatures. But Python's type system can't express "returns a wrapper with the same signature as the input." You can use `cast()` to pretend it works, but that's a lie. The type checker can't verify it.

So we changed our goal: decorators now return the original function unchanged. They register wrappers internally, but the return value is the input function. This is something Python's types can verify. Problem solved, no lies.

This principle matters because lies accumulate. Each `cast()` is a place where the type checker stops helping you. When you change code, it can't catch mistakes. You're on your own.

If your types fight you, stop and ask: "Am I solving the right problem?" Often the answer is no.

## Minimal API by Design

We export exactly five names: `TypedTyper`, `run`, `Argument`, `Option`, `Exit`. That's it.

This isn't an oversight. We're not building a full-featured CLI framework. We're building a boundary layer between Typer and VicePython. The smaller the surface, the less that can break, and the easier it is to maintain.

We won't add `OptionInt`, `OptionBool`, or other specialty helpers. Use `Annotated[int, Option(...)]`. We won't wrap `typer.prompt()` or `typer.confirm()`. Import them directly. We won't provide validation decorators or middleware hooks. Those are orthogonal concerns.

If you need features we don't wrap, import Typer directly:

```python
import typer

@app.command_result()
def login(username: str) -> Result[None, LoginError]:
    password = typer.prompt("Password", hide_input=True)
    # ...
```

This is expected and fine. We're not trying to hide Typer from you—we're just quarantining its types at the boundary.

## When to Use This Library

Use this library when:
- You're writing more than one CLI tool
- You're following VicePython conventions
- You want consistent error handling across tools
- You value testability and debuggability

Don't use this library when:
- You're writing a one-off script
- You're comfortable with Typer's semantics everywhere
- You don't care about Result types

We built this for teams standardizing on VicePython. If that's not you, plain Typer is probably simpler.

## Trade-Offs We Accepted

**Pro:** Clean semantics, testability, consistency across tools.

**Con:** Another layer to understand, slight overhead on first command invocation, can't use all Typer features directly.

We think the trade-off is worth it for maintainable CLIs, but it's not free. You're learning a wrapper instead of using the framework directly. You're debugging through an extra layer if something goes wrong. And if Typer releases a feature we don't wrap, you'll either import it directly or wait for us to add support.

These are real costs. We minimize them by keeping the wrapper small, but they don't disappear.

## Exit Strategy

If Typer evolves to support `Result` semantics natively, or if VicePython conventions change significantly, we'll deprecate this library. The goal is containment, not permanence.

We're not trying to own CLI development. We're solving a specific impedance mismatch. If that mismatch goes away, so should this library.
