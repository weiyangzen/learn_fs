# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_nexttoward.c

Implements double `nexttoward(double x, long double y)` for systems with 15-bit long-double exponents.

Key behavior: checks NaNs across double and long double, returns `(double)y` on equality, steps `x` by one double ulp toward long-double `y`, and raises overflow/underflow via arithmetic.

Important dependencies: `<machine/ieee.h>`, `math_private.h`, and `union ieee_ext_u`.

Notable risks: unsupported when `LDBL_MAX_EXP != 0x4000`; direction comparison mixes double and long double.
