# SESSION START CHECKLIST

**Before doing ANY work, complete this checklist:**

☐ 1. Load vicepython principles from ~/.claude/skills/vicepython.md
☐ 2. Read all Global Requirements below
☐ 3. Read Naming Hygiene rules (Non-negotiable)
☐ 4. Understand the TDD workflow: RED → GREEN → REFACTOR
☐ 5. Create a list of implementation steps and present for approval

**CRITICAL:** Do NOT write any code until checklist is complete and steps are approved.

# Context

By default typer/click CLIs with only one command behave like a command:

mycli -> runs the command
mycli something -> something is treated as an argument

There is a concept of "group" for commands with more than one subcommand.

We want to support enforcing group for commands with only one subcommand.

Under some circumstances, users do want single-command tool semantics: running mycli executes the tool's only command

We also want to support subcommand-first tool semantics: running mycli on its own never executes work (but does invoke help); users must type prog <command> to do something.

Typer does not give us a clean "always treat this as a group even if there is only one command" switch without forcing the group shape.

Forcing the group shape is typically done by registering a callback, even if it's a no-op.

We should support both behaviours explicitly in vicepython-ffi-typer:

- TypedTyper(..., require_subcommand=False) (default) - single-command tools behave like single commands
- TypedTyper(..., require_subcommand=True) - force single-command tools to behave like multi-command tools (groups):
  - internally ensure the root is a group (by registering an internal no-op callback)
  - set no_args_is_help=True so prog prints help and exits (rather than running anything)

We should be explicit in the docs, and say:

When require_subcommand=True we force group behaviour by installing an internal no-op callback. This is an implementation detail to achieve stable invocation semantics.

# Design Decisions (Approved)

## 1. Parameter API Design - Option B
Keep both `require_subcommand` and `no_args_is_help` in the public API.

**Implementation:**
- `TypedTyper(..., require_subcommand=False, no_args_is_help=False)` - both parameters exposed
- When `require_subcommand=True`, force `no_args_is_help=True` internally
- Logic: `no_args_is_help=require_subcommand or no_args_is_help`

**Rationale:**
- `require_subcommand` is semantic ("must type a subcommand")
- Allowing `no_args_is_help=False` with `require_subcommand=True` would be confusing UX
- Forcing the coupling gives stable, friendly default behavior

**Documentation:**
Must clearly document: "When require_subcommand=True, no_args_is_help is forced to True"

**Edge case behavior:**
If user explicitly sets `require_subcommand=False, no_args_is_help=True`, the logic `no_args_is_help=require_subcommand or no_args_is_help` will honor the True value. This is correct behavior - user explicitly requested help on no args.

## 2. Test Coverage
Use Surface 1 (Programmatic harness) tests only - no subprocess needed for this library-level feature.

**Test cases:**
1. Single-command + `require_subcommand=False` (default):
   - `run(app, ["prog"])` → executes the command (current Typer behavior; pin it)

2. Single-command + `require_subcommand=True`:
   - `run(app, ["prog"])` → prints help and exits 0 (no_args_is_help behavior)
   - `run(app, ["prog", "doctor"])` → executes the command

3. Multi-command app:
   - `run(app, ["prog"])` → shows help or errors (must NOT run a default command)
   - `run(app, ["prog", "doctor"])` → executes the command

All tests use `capsys: pytest.CaptureFixture[str]` and call `run(app, argv)` directly.

## 3. Internal Callback Registration - Option B
Call `self._app.callback()` directly (bypass our public wrapper).

**Rationale:**
- This internal callback exists only to force group shape
- Not part of supported public surface
- Bypassing wrapper makes it clear this is an implementation detail

**Requirements:**
- Callback name must be clearly private: `_vp_internal_callback`
- No help text
- Never prints or exits

## 4. Documentation Placement
Put it in **both** locations:

1. **`TypedTyper.__init__` docstring:** Short and explicit (1–2 sentences)
2. **README:** Short note in a "Behavior knobs" or similar section

Do NOT create a separate concepts doc (overkill for this feature).

# Implementation Steps

Following TDD (RED → GREEN → REFACTOR):

## Step 1: RED - Write failing tests

Create `tests/test_require_subcommand.py` implementing the three test cases specified in "## 2. Test Coverage" above.

**CRITICAL ARGV RULES for these tests:**

1. **Single-command + default behavior (`require_subcommand=False`):**
   - DO: `run(app, ["prog"])` - no command name, just program name
   - DON'T: `run(app, ["prog", "doctor"])` - this would pass "doctor" as an argument

2. **Single-command + forced group behavior (`require_subcommand=True`):**
   - DO: `run(app, ["prog", "doctor"])` - command name IS required (group semantics)
   - For help: `run(app, ["prog"])` - no command name shows help

3. **Multi-command apps:**
   - ALWAYS: `run(app, ["prog", "commandname"])` - command name required

All tests use `capsys: pytest.CaptureFixture[str]`.

**Run tests - they should fail.** Stop and request human review.

## Step 2: GREEN - Implement minimum code

Modify `src/vicepython_ffi_typer/typed_typer.py`:

1. Add `require_subcommand: bool = False` parameter to `TypedTyper.__init__`
2. Store it: `self._require_subcommand = require_subcommand`
3. Update `no_args_is_help` logic: `no_args_is_help = require_subcommand or no_args_is_help`
4. When `require_subcommand=True`, register internal no-op callback to force group behavior:
   ```python
   if self._require_subcommand:
       # Force group behavior by registering internal callback
       # This must happen in __init__ before any commands are registered
       @self._app.callback()
       def _vp_internal_callback() -> None:
           """Internal callback to force group behavior. Do not use directly."""
           pass
   ```
   **IMPORTANT:** This decorator syntax works because `self._app.callback()` returns a decorator function. The inner function `_vp_internal_callback` gets registered as the callback. This is standard Typer/Click API usage.

5. Update `__init__` docstring with 1-2 sentence explanation including the edge case behavior

Run tests until they pass. When green, commit with commit-message-writer agent.

## Step 3: REFACTOR - Review and improve

1. Review diff against VicePython standards
2. Check for:
   - Type annotations complete and correct
   - No builtin shadowing
   - Clear naming
   - Minimal changes only
3. Update README.md with behavior knob documentation
4. Run mypy --strict and pytest
5. If changes made, commit with commit-message-writer agent

## Step 4: Final verification

- Run full test suite: `uv run pytest`
- Run type checker: `uv run mypy --strict src/ tests/`
- Verify all tests pass
- Feature complete

# Naming Hygiene (Non-negotiable)

- Do NOT shadow Python builtins or keywords anywhere.
  This includes (but is not limited to):
  id, type, list, dict, set, str, int, error, file, input, output.

- In domain models:
  - Use explicit names like:
    - node_id, outcome_id, next_id
    - node_type, anomaly_type
  - Never use `id` or `type` as field names.

- In pattern matching:
  - Do not bind names like `error` or `list`.
  - Use `err`, `exc`, or descriptive names.

Violations of this rule are considered **design errors**, not style issues.

# Development process

Follow red, green, refactor as a process:

1) RED: Write a failing test that will demonstrate the next slice of functionality we want to deliver. Run the test, if it fails, good. **STOP HERE - ask the human to run the tests and review them. Wait for feedback before continuing.**
2) GREEN: Write the minimum code to make the test pass. Do the simplest thing that could possibly work. Run the test. If it fails, iterate until it passes. If it passes, use the **commit-message-writer agent** to generate a commit message from the diff and commit, and move to:
3) REFACTOR: Look at the diff of what you have done. Evaluate it against the vicepython standards. Look for architectural smells, violations, opportunities to DRY up. Make changes... run tests until they pass. When they pass, use the **commit-message-writer agent** to commit if changes were made. This feature is complete.

When writing a test to verify this works:

## MANDATORY CLI ENTRYPOINT & TESTING RULES

These rules apply to ALL CLI applications in this codebase.

There are EXACTLY THREE CLI entrypoint surfaces.
Each surface exists for a different reason.
Each surface has EXACTLY ONE allowed testing strategy.

Do not invent alternatives.
Do not collapse surfaces.
Do not skip required surfaces.

### SURFACE 1: Programmatic harness entrypoint (REQUIRED)

**Definition:**
- Invocation via direct call to the CLI harness:
  `run(app, argv)`

**Purpose:**
- Validate command registration
- Validate handler behaviour
- Validate exit code semantics
- Validate stdout/stderr output

**Rules:**
- This surface MUST exist in every CLI project.
- This surface MUST be tested.
- This test MUST NOT use subprocess.
- This test MUST use pytest `capsys`.
- This test MUST import `app` and call `run(app, argv)` directly.
- **Type annotation:** Use `pytest.CaptureFixture[str]`, NOT `Any`
- **IMPORTANT ARGV RULES:**
  - Single-command + default (`require_subcommand=False`): `["prog"]` - no command name
  - Single-command + forced group (`require_subcommand=True`): `["prog", "cmdname"]` - command name required
  - Multi-command apps: `["prog", "cmdname"]` - command name always required

Failure to test this surface is a TESTING ERROR.

**Example:**
```python
def test_doctor_command(capsys: pytest.CaptureFixture[str]) -> None:
    """Test compass doctor returns expected output."""
    exit_code = run(app, ["compass"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == "the doctor is in the house\n"
```

### SURFACE 2: Module entrypoint (REQUIRED)

**Definition:**
- Invocation via:
  `python -m <package> <command>`

**Purpose:**
- Validate `__main__.py` wiring
- Validate argv plumbing at the module level

**Rules:**
- Every CLI package MUST define `<package>/__main__.py`.
- `__main__.py` MUST call the same harness:
  `raise SystemExit(run(app, sys.argv))`
- This surface MUST be tested.
- This test MUST use subprocess.
- This test MUST assert exit code and stdout.

Failure to test this surface is a TESTING ERROR.

**Example `src/compass/__main__.py`:**
```python
"""Module entrypoint for compass CLI."""

import sys
from compass.adapters.cli import app
from vicepython_ffi_typer import run

if __name__ == "__main__":
    raise SystemExit(run(app, sys.argv))
```

**Example test:**
```python
def test_module_entrypoint_smoke() -> None:
    """Test python -m compass invocation."""
    result = subprocess.run(
        [sys.executable, "-m", "compass"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "the doctor is in the house" in result.stdout
```

### SURFACE 3: Distribution / tooling entrypoint (REQUIRED IF ADVERTISED)

**Definition:**
- Invocation via console script:
  e.g. `uv run <binary> <command>`

**Purpose:**
- Validate `[project.scripts]` wiring
- Validate that the console script resolves to the correct callable

**Rules:**
- If the project advertises a console script in pyproject.toml,
  this surface MUST exist.
- If this surface exists, it MUST be tested.
- This test MUST use subprocess.
- This test MUST be marked with `@pytest.mark.dist`.
- This test MUST NOT be the only end-to-end test.

Failure to test this surface when advertised is a PACKAGING ERROR.

**Example `pyproject.toml`:**
```toml
[project.scripts]
compass = "compass.adapters.cli:main"
```

**Example `cli.py` addition:**
```python
def main() -> int:
    """Entry point for the compass CLI."""
    return run(app, sys.argv)
```

**Example test:**
```python
@pytest.mark.dist
def test_distribution_entrypoint_smoke() -> None:
    """Test uv run compass invocation."""
    result = subprocess.run(
        ["uv", "run", "compass"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "the doctor is in the house" in result.stdout
```

### CONVERGENCE RULE

All entrypoints MUST converge on the SAME harness.

- No entrypoint may duplicate command logic.
- No entrypoint may bypass `run()`.
- No entrypoint may call handlers directly.

There MUST be exactly one place where:
- commands are registered
- handlers are defined

### ENTRYPOINT RULE

- Command handlers MUST return Result[T, E].
- Entry point functions (main, __main__) MUST return int (exit code).
- Entry points MUST NOT return Result.
- Only the CLI harness converts Result → exit code.

### TESTING SUMMARY (NON-NEGOTIABLE)

Every CLI project MUST have:
- ≥1 harness test (Surface 1)
- ≥1 module entrypoint smoke test (Surface 2)

IF a console script is advertised:
- ≥1 distribution smoke test (Surface 3)

Tests MUST be minimal.
Tests MUST assert behaviour, not implementation.
Tests MUST fail if wiring breaks.
