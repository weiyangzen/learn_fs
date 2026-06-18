# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtopdd.c

Purpose: Parses a string into double-double storage.

Core behavior:
- Uses a 106-bit `FPI`.
- Calls `strtodg` and packs the result as two doubles.
- Handles normal, denormal subcases, infinity, NaN, and sign propagation to both doubles.
- Splits the high and low portions of the significand into two IEEE double encodings.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses optional `gdtoa_fltrnds.h`, `strtodg`, and `hi0bits`.
