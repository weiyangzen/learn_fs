# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_fmaxl.c

Implements long-double `fmaxl()` with direct extended-format inspection.

Key behavior: clears the explicit integer bit before NaN checks, returns the non-NaN operand, handles signed zero by returning the positive value, then compares normally.

Important dependencies: `<machine/ieee.h>`, `union ieee_ext_u`, and `memset`.

Notable risks: assumes extended-format field names and integer-bit conventions.
