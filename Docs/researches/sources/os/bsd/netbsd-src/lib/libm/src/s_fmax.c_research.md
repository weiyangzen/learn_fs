# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_fmax.c

Implements double `fmax()` with explicit NaN and signed-zero handling.

Key behavior: returns the non-NaN operand if exactly one input is NaN; when signs differ, returns positive zero over negative zero; otherwise uses `x > y`.

Important dependencies: `<machine/ieee.h>` and `union ieee_double_u`.

Notable risks: direct union field checks are machine IEEE-layout dependent.
