# File Research: sources/os/plan9/plan9/sys/src/cmd/8c/div.c

## Purpose
Generates optimized division and modulus by invariant integer constants for the 386 backend.

## Key Functions
- `multiplier()` computes magic multipliers using the Granlund-Montgomery algorithm.
- `sdiv()` and `udiv()` derive signed/unsigned multiplier and shift parameters.
- `sdivgen()` emits signed division by constant using multiply-high and correction.
- `udivgen()` emits unsigned division by constant, including pre-shift paths.
- `sext()` emits sign extension into a helper register or `DX`.
- `sdiv2()` optimizes signed division by powers of two.
- `smod2()` optimizes signed modulus by powers of two.

## Important Behavior
- Avoids expensive hardware division where constant divisors permit multiply/shift sequences.
- Handles negative signed divisors by negating the final quotient.
- Handles signed modulus correction so C semantics are preserved for negative dividends.
- Cooperates with `cgen.c`, which calls these helpers when it detects constant divisors.

## Research Notes
This is arithmetic-strength reduction for a CPU where division is relatively costly.
