# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zmath.c

## Purpose
Implements mathematical PostScript operators and the interpreter random-number generator.

## Key Functions
- `zsqrt()`, `zarccos()`, `zarcsin()`, `zatan()`, `zcos()`, `zsin()`, `zexp()`, `zln()`, and `zlog()` implement numeric functions.
- `zrand()`, `zsrand()`, and `zrrand()` implement Adobe-compatible random state operations.

## Important Behavior
- Public operator functions are also used by FunctionType 4 calculator support.
- Trig functions use degrees for PostScript semantics.
- `exp` rejects `0 0 exp` and negative bases with non-integer exponents.
- Random generation uses the Park-Miller `16807 mod (2^31 - 1)` algorithm.
- Random state is stored in interpreter context so context switching can preserve it.

## Research Notes
Pure arithmetic interpreter support.
