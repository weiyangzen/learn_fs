# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtordd.c

Purpose: Parses with an explicit rounding mode into double-double storage.

Core behavior:
- `ULtodd()` packs a 106-bit significand into two double words.
- Handles normal splitting, denormal subcases, infinity, NaN, NaN payload, and sign.
- `strtordd()` chooses a 106-bit `FPI`, optionally overrides rounding, calls `strtodg`, then packs via `ULtodd`.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `strtodg`, `hi0bits`, generated double NaN constants, and endian word macros.
