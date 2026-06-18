# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_logbl.c

Implements long-double `logbl()`.

Key behavior: returns `-inf` for zero, absolute value for NaN/Inf, scales subnormals to normal range, and returns exponent minus extended bias.

Important dependencies: `namespace.h`, `<machine/ieee.h>`, `fabsl`, `union ieee_ext_u`, and `FROM_UNDERFLOW`.

Notable risks: supports only 64- and 113-bit long-double mantissas.
