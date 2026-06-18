# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/gdtoa/gd_qnan.h

Alpha gdtoa quiet-NaN constants.

Key behavior:
- Defines single-precision quiet NaN `f_QNAN`.
- Defines little-endian double quiet NaN words `d_QNAN0` and `d_QNAN1`.

Dependencies:
- Alpha little-endian floating-point layout.
