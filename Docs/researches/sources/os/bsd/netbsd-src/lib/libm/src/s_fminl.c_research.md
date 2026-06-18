# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_fminl.c

Implements long-double `fminl()` with extended-format NaN and signed-zero handling.

Key behavior: clears the explicit integer bit before NaN checks, returns the non-NaN operand, returns negative zero when signs differ, and otherwise compares normally.

Important dependencies: `<machine/ieee.h>`, `union ieee_ext_u`, and `memset`.

Notable risks: long-double field assumptions are format-specific.
