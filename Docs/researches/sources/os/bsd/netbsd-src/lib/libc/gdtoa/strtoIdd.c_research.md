# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtoIdd.c

Purpose: Parses a string into a double-double interval.

Core behavior:
- Uses a 106-bit `FPI`, with sudden-underflow parameters adjusted by platform.
- Calls `strtoIg` to obtain exact or bounding `Bigint` endpoints.
- Packs endpoints into two-double representations with `ULtodd`.
- Duplicates the first endpoint if no second endpoint is needed.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `Balloc`, `Bfree`, `strtoIg`, and `ULtodd`.
