# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtoIf.c

Purpose: Parses a string into a single-precision interval.

Core behavior:
- Uses IEEE float `FPI {24, ...}`.
- Calls `strtoIg` to compute exact or adjacent interval bounds.
- Packs endpoints into float storage with `ULtof`.
- Copies the exact endpoint into both outputs when no interval widening is needed.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `Balloc`, `Bfree`, `strtoIg`, and `ULtof`.
