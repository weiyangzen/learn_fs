# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtopx.c

Purpose: Parses a string into 80-bit extended storage represented by five `UShort`s.

Core behavior:
- Defines endian-specific five-word layout.
- Uses `FPI {64, ...}` and `strtodg`.
- Packs zero, denormal, normal, infinity, NaN, and NaN payload results.
- Sets sign in the exponent word.
- Uses generated `ldus_QNAN*` constants for plain NaN.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses optional `gdtoa_fltrnds.h` and `strtodg`.
