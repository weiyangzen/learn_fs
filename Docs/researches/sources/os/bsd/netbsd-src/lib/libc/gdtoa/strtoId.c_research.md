# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtoId.c

Purpose: Parses a string into a double-precision interval.

Core behavior:
- Uses IEEE double `FPI {53, ...}`.
- Calls `strtoIg` to get one exact endpoint or two adjacent endpoints around an inexact value.
- Packs endpoints into `double` storage with `ULtod`.
- Copies the first endpoint to the second when parsing is exact.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `Balloc`, `Bfree`, `strtoIg`, and `ULtod`.
