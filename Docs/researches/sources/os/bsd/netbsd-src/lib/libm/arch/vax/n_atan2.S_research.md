# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/vax/n_atan2.S

## Scope

Implements VAX `atan2`, `atan2f`, and `atan2l` aliases in assembly for D-format arithmetic, including reserved-operand handling and quadrant/sign logic.

## APIs And Behavior

- `_atan2f` converts float arguments to double, calls `_atan2`, and converts the result back to float.
- `_atan2` and `_atan2l` share the double implementation.
- Rejects VAX reserved operands by returning the reserved operand pattern.
- Handles zero `y`, zero `x`, large exponent differences, and sign of `x` / `y` explicitly.
- Reduces `t = |y/x|` into ranges around `0`, `1/2`, `1`, `3/2`, and infinity, then evaluates an odd polynomial table for arctangent correction.
- Applies `pi - t`, `pi/2`, and sign restoration for the final quadrant.

## Dependencies And Risks

- Depends on VAX reserved-operand encoding and D-format exponent extraction.
- Polynomial constants and branch intervals drive accuracy.
- Special-case comments mention NaN/INF semantics, but VAX uses reserved operands rather than IEEE NaNs/infinities.
