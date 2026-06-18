# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtopxL.c

Purpose: Parses a string into 80-bit extended storage represented by three `ULong`s.

Core behavior:
- Defines endian-specific three-word layout.
- Uses `FPI {64, ...}` and `strtodg`.
- Packs zero, normal, denormal, infinity, NaN, and NaN payload values.
- Sets sign in the high exponent word.
- Uses generated `ld_QNAN*` constants for plain NaN.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses optional `gdtoa_fltrnds.h` and `strtodg`.
