# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtoIxL.c

Purpose: Parses a string into an interval for 80-bit extended format stored as three `ULong`s.

Core behavior:
- Uses `FPI {64, ...}`.
- Calls `strtoIg` for exact or adjacent interval endpoints.
- Packs endpoints with `ULtoxL`.
- Copies the first endpoint to the second when exact.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `Balloc`, `Bfree`, `strtoIg`, and `ULtoxL`.
