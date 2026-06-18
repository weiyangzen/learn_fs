# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtoIQ.c

Purpose: Parses a string into a quad-precision interval.

Core behavior:
- Uses `FPI {113, ...}` for IEEE quad precision.
- Allocates a first `Bigint` result buffer and calls `strtoIg`.
- Converts lower/upper interval endpoints with `ULtoQ`.
- If parsing is exact, duplicates the first endpoint into the second.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `Balloc`, `Bfree`, `strtoIg`, and `ULtoQ`.
