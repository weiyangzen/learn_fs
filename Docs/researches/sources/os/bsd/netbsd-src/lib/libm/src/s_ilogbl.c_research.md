# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_ilogbl.c

Implements long-double `ilogbl()`.

Key behavior: raises invalid for zero, NaN, and infinity; scales subnormals by a format-dependent power to normalize; returns exponent minus extended bias.

Important dependencies: `namespace.h`, `fenv.h`, `<machine/ieee.h>`, `union ieee_ext_u`, and `FROM_UNDERFLOW`.

Notable risks: supports only `LDBL_MANT_DIG == 64` or `113`.
