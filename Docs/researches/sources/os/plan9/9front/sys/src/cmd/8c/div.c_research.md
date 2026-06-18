# File Research: sources/os/plan9/9front/sys/src/cmd/8c/div.c

This file optimizes integer division and modulo by invariant constants for 386 code generation.

Key responsibilities:
- Implements Granlund-Montgomery style magic-multiplier calculation in `multiplier()`.
- `sdiv()` and `udiv()` compute signed/unsigned magic multipliers, shifts, and adjustment flags.
- `sdivgen()` and `udivgen()` emit quotient-generation instruction sequences using multiply-high results in `DX`.
- `sext()` obtains sign-extension masks, using `CDQ` when possible.
- `sdiv2()` and `smod2()` optimize signed division/modulo by powers of two, including correction for negative dividends.

Integration points:
- Called from `cgen.c` for constant `ODIV`, `OMOD`, `OLDIV`, and assignment variants.
- Emits instructions through `gins()` and uses register allocation from `txt.c`.
- Assumes x86 multiply/divide conventions around `AX`/`DX`.

Risks and invariants:
- Correctness depends on unsigned/signed edge cases, especially negative divisors and `0x80000000`.
- Power-of-two signed modulo must preserve C semantics for negative operands.
