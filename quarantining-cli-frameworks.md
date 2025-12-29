Title: Quarantining CLI Frameworks at the Boundary (vicepython-ffi-typer)

Status: Proposed

Pattern Name
Quarantined CLI Boundary

Context
You are building multiple small and medium-sized command-line tools that interact with core domain logic. These tools are long-lived, will be modified over time, and are increasingly written or assisted by LLMs. You want consistent behaviour, predictable failure semantics, and code that remains easy to reason about as it evolves.

A modern CLI framework (e.g. Typer/Click) offers good ergonomics and UX, but its typing and control-flow conventions do not align with VicePython’s semantics (explicit Result/Option, no implicit None, no exception-driven logic in core code).

Problem
If each CLI integrates directly with the framework:
- Optional/None values and exceptions leak into domain logic.
- Error handling and exit behaviour become inconsistent across tools.
- Boundary glue is reimplemented repeatedly, slightly differently each time.
- LLMs reproduce these inconsistencies at scale, producing “semi-products” that look correct but are semantically muddy.

If the framework is avoided entirely:
- CLI development becomes unpleasant.
- Teams revert to inline shell or ad-hoc scripts.
- UX quality drops and adoption suffers.

Forces
- We want ergonomic CLIs, but not at the cost of semantic clarity.
- We want strong typing and explicit failure, but CLI frameworks are not built that way.
- We want to move fast, but repeated boundary glue creates long-term drag.
- We want to avoid inventing a framework, but we also want to avoid unconstrained usage.
- We want an escape hatch if the ecosystem improves.

Solution
Introduce a small, opinionated wrapper library that quarantines the CLI framework at the boundary.

The pattern has three elements:
1. A minimal harness that owns all interaction with the CLI framework.
2. A contract that command handlers return Result values instead of raising or printing.
3. A single run boundary that handles printing, exit codes, and unexpected failures.

This wrapper is intentionally small:
- It does not reimplement the CLI framework.
- It exposes only the minimal surface needed to define commands and run the app.
- It converts Optional inputs at the boundary into Option/Result before calling domain code.

Resulting Context
- Domain and application code remains free of CLI framework concerns.
- Error semantics are explicit and uniform across all tools.
- LLM-assisted code generation is constrained to follow the same executable pattern.
- CLI UX remains good, but its complexity is localised.
- Future changes to the CLI framework affect one place, not many repositories.

Applicability
Use this pattern when:
- You are building more than one CLI tool.
- Tools are expected to evolve over time.
- Semantic correctness and debuggability matter.
- You want to standardise behaviour across an organisation.

Do not use this pattern when:
- You are writing a one-off script with no expected evolution.
- You are happy to accept framework-specific semantics throughout the codebase.
- You control neither the CLI framework nor the surrounding standards.

Consequences
Positive:
- Reduced semantic drift at boundaries.
- Fewer bespoke patterns and less review friction.
- Clear teaching story for humans and LLMs.
- Easier deletion or replacement later.

Negative:
- A small, ongoing maintenance cost to track the CLI framework.
- A risk of wrapper growth if discipline is not maintained.

Guardrails
- The wrapper’s public API must remain minimal and opinionated.
- New features are added only in response to repeated, real usage pressure.
- The wrapper must not become a general-purpose framework.
- Versions of the underlying CLI framework are pinned and upgraded deliberately.

Exit Strategy
If the CLI framework (or an alternative) evolves to support VicePython semantics natively, or if CLI usage patterns change significantly, this wrapper should be deprecated and removed. The goal is containment, not permanence.

Related Patterns
- Explicit Boundary Conversion (Optional → Option, exceptions → Result)
- Protocol Decoder (external semantics → explicit states)
- Small Tools, Strong Semantics (VP0/VP1 discipline)
