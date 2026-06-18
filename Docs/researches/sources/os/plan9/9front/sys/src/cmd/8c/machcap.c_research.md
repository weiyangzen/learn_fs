# File Research: sources/os/plan9/9front/sys/src/cmd/8c/machcap.c

This small file declares which operations the 386 backend can handle directly, especially for long and vlong expressions.

Key responsibilities:
- `machcap()` returns whether a node operation is supported by machine-specific generation.
- Enables direct support for multiply, bitwise/arithmetic ops, shifts, casts, conditionals, logical expressions, assignment arithmetic, increments/decrements, and comparisons.
- Handles special mixed-assignment cases by rejecting some `mixedasop()` combinations.
- A `Z` node query returns true as a general capability test.

Integration points:
- Used by shared compiler logic to decide whether machine-specific code generation is available.
- Works with `cgen64.c` and `sgen.c` decisions around vlong operations and addressability.

Risks and invariants:
- Overstating capability can route unsupported nodes into backend paths.
- Understating capability can force less optimal or unavailable generic handling.
