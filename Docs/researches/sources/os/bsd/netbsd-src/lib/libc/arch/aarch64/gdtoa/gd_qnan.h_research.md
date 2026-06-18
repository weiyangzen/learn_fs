# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/gdtoa/gd_qnan.h

AArch64 gdtoa quiet-NaN constants.

Key behavior:
- Defines single-precision quiet NaN word `f_QNAN`.
- Defines double and long-double quiet-NaN word layouts differently for big-endian and little-endian AArch64.

Dependencies:
- `__AARCH64EB__` target-endian macro.
