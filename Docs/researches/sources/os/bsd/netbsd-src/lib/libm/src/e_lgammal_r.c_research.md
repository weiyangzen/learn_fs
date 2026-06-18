# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_lgammal_r.c

This file is the long-double dispatch layer for `lgammal_r(long double, int *)`.

When `__HAVE_LONG_DOUBLE` is defined, it selects the implementation by `LDBL_MANT_DIG`: 64-bit mantissa includes `../ld80/e_lgammal_r.c`, 113-bit mantissa includes `../ld128/e_lgammal_r.c`, and other formats are rejected at compile time. Without long-double support, it falls back to `lgamma_r(double, int *)`.

It weak-aliases `lgammal_r` to `_lgammal_r` and depends on machine floating-point format headers.
