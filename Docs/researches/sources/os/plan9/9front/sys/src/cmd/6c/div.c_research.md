# File Research: sources/os/plan9/9front/sys/src/cmd/6c/div.c

This file implements optimized amd64 code generation for division and modulo by invariant 32-bit integer constants, based on Granlund and Montgomery’s multiplication method.

Key elements:
- `multiplier()` computes a magic multiplier and shift amount for a divisor.
- `sdiv()` derives signed-division multiplier/shift metadata and whether an add adjustment is needed.
- `udiv()` derives unsigned-division metadata, including pre-shift handling for even divisors and adjustment cases.
- `sdivgen()` emits signed constant-division code using `IMULL`, high-half result in `DX`, sign correction, shift, and optional negation.
- `udivgen()` emits unsigned constant-division code using `MULL`, optional pre-shift, adjustment add/rotate, and final shift.
- `sext()` materializes the sign extension of a value, using `CDQ` when source is `AX` and `DX` is available.
- `sdiv2()` optimizes signed division by powers of two with bias correction and arithmetic shift.
- `smod2()` optimizes signed modulo by powers of two with sign correction.

Dependencies and integration:
- Called from `cgen.c` for scalar divide/modulo and compound divide/modulo when the divisor is a suitable constant.
- Uses backend emitters and register helpers from `gc.h`.

Notable behavior:
- Power-of-two signed division/modulo is handled separately from general magic-multiplier division.
- Negative signed divisors are handled by generating a positive division then negating the quotient where needed.
- The implementation is limited to 32-bit-style constant division paths used by `typechl` cases in `cgen.c`.

Research notes:
- This file is a small but performance-sensitive backend optimization module.
