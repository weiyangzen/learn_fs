# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_nextafterl.c

Implements long-double `nextafterl()` and aliases `nexttowardl()` to it.

Key behavior: handles NaNs, equality, signed zero to min-subnormal, one-ulp significand stepping, explicit integer-bit handling, m68k special cases, overflow, and underflow.

Important dependencies: `<machine/ieee.h>`, `union ieee_ext_u`, `LDBL_NBIT`, `mask_nbit_l`, and volatile long-double arithmetic.

Notable risks: architecture-specific integer-bit handling is delicate, especially around subnormals.
