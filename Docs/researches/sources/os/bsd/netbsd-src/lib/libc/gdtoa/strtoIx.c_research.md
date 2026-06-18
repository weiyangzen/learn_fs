# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtoIx.c

Purpose: Parses a string into an interval for 80-bit extended format stored as five `UShort`s.

Core behavior:
- Uses `FPI {64, ...}` for 64-bit precision extended format.
- Calls `strtoIg` for exact or adjacent endpoint bits.
- Packs endpoints with `ULtox`.
- Copies the first endpoint to the second when exact.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `Balloc`, `Bfree`, `strtoIg`, and `ULtox`.
