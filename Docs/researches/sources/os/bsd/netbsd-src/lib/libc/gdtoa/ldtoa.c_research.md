# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/ldtoa.c

Purpose: Provides `ldtoa()` as a `long double` wrapper around `gdtoa()`.

Core behavior:
- Builds an `FPI` from `LDBL_MANT_DIG`, `LDBL_MIN_EXP`, and `LDBL_MAX_EXP`.
- Extracts sign, binary exponent, and significand bits using machine long-double layout macros.
- Classifies zero, normal, subnormal, infinity, and NaN.
- Sets implicit integer/significand bits when required by the platform format.
- Converts through `gdtoa()` and maps `gdtoa`'s `-32768` special decimal point to `INT_MAX`.
- Falls back to casting through `double` when no extended long double is available.

Dependencies:
- Uses `<machine/ieee.h>`, `<float.h>`, `<math.h>`, and `gdtoaimp.h`.
- Depends on `EXT_TO_ARRAY32` and related machine floating-point layout macros.
