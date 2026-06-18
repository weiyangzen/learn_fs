# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_modfl.c

Implements long-double `modfl()` by masking high or low significand words.

Key behavior: handles integer part in high significand, low significand, and no-fraction cases; preserves signed zero through a static zero array; returns NaN fractional part unchanged.

Important dependencies: `namespace.h`, `<machine/ieee.h>`, `LDBL_MANT_DIG`, `EXT_FRACLBITS`, and `union ieee_ext_u`.

Notable risks: `GETFRAC` and mask widths depend on exact extended-format storage.
