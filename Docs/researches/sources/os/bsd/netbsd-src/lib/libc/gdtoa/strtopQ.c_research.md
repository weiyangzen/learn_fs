# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtopQ.c

Purpose: Parses a string into quad-precision binary storage.

Core behavior:
- Defines endian-specific four-word layout.
- Uses `FPI {113, ...}` and `strtodg`.
- Packs zero, normal, denormal, infinity, NaN, and NaN payload results.
- Sets the sign bit from `STRTOG_Neg`.
- Uses generated long-double quiet-NaN words for plain NaN.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses optional `gdtoa_fltrnds.h`, `strtodg`, and `ld_QNAN*` constants.
