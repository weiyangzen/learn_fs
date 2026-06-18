# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtodg.c

Purpose: Generic decimal/hex string parser for arbitrary binary formats described by `FPI`.

Core behavior:
- Provides helper routines `increment`, `decrement`, `all_on`, `set_ones`, `rvOK`, and `mantbits`.
- Parses whitespace, sign, decimal digits, locale decimal point, decimal exponent, hex floats, infinity, and NaN payloads.
- Produces result class flags, inexact direction flags, exponent, and packed significand words.
- Uses fast native-double approximation when possible and exact `Bigint` refinement otherwise.
- Handles all rounding modes, overflow, underflow, gradual/sudden underflow, denormal normalization, and boundary transitions.
- Used as the central parser by `strtof`, `strtod` wrappers, `strtop*`, `strtor*`, and interval APIs.

Dependencies:
- Includes `gdtoaimp.h` and optionally `locale.h`.
- Uses `gethex`, `hexnan`, `s2b`, `d2b`, `copybits`, `pow5mult`, `ratio`, `trailz`, `sum`, `diff`, and `errno`.
