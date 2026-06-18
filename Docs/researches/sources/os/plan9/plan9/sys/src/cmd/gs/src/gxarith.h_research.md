# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxarith.h

Purpose: Defines arithmetic helpers and declares integer arithmetic utilities.

Key definitions:
- `any_abs(x)` generic signed absolute macro.
- `fits_in_bits()` and `fits_in_ubits()` integer bit-fit tests.
- Floating comparison/fit macros: `is_fzero`, `is_fzero2`, `is_fneg`, `is_fge1`, `f_fits_in_bits`, `f_fits_in_ubits`.
- `small_exact_log2()` lookup macro for powers of two up to 128.

Declared functions:
- `imod()`, `igcd()`, `idivmod()`, and `ilog2()`.

Behavior:
- `imod()` promises non-negative modulo independent of implementation-defined negative `%` behavior.
- Comments document a quotient/remainder optimization for values modulo `2^n - 1`.

Dependencies:
- Assumes Ghostscript scalar typedefs and architecture constants are available.

Notable risks:
- Several macros evaluate expressions in arithmetic contexts and may overflow if called outside expected ranges.
