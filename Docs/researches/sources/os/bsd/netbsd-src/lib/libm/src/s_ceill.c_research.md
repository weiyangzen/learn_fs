# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_ceill.c

Implements `ceill()` for real long double by manipulating `union ieee_ext_u` exponent and fraction fields. It handles both implicit and explicit integer-bit long-double layouts.

Key behavior: rounds toward positive infinity, preserves signed zero for negative magnitudes below 1, increments positive fractional values across high/low significand words, and raises inexact via `huge + x`.

Important dependencies: `namespace.h`, `<machine/ieee.h>`, `LDBL_IMPLICIT_NBIT`, `EXT_FRACHBITS`, and `EXT_FRACLBITS`.

Notable risks: carry handling in `INC_MANH` is layout-sensitive; unsupported long-double formats are not covered.
