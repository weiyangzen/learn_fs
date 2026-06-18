# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_fminf.c

Implements float `fminf()` with explicit NaN and signed-zero behavior.

Key behavior: returns the non-NaN operand without raising comparison exceptions and returns negative zero when comparing opposite-signed zeroes.

Important dependencies: `<machine/ieee.h>` and `union ieee_single_u`.

Notable risks: relies on NetBSD single-precision bitfield layout.
