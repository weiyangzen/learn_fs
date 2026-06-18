# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_fmin.c

Implements double `fmin()` with NaN suppression and signed-zero handling.

Key behavior: returns the non-NaN operand if only one input is NaN; when signs differ, returns negative zero; otherwise uses `x < y`.

Important dependencies: `<machine/ieee.h>` and `union ieee_double_u`.

Notable risks: direct IEEE field access is target-dependent.
