# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtorf.c

Purpose: Parses with an explicit rounding mode into float storage.

Core behavior:
- `ULtof()` packs `strtodg` bits and result class into an IEEE float word.
- `strtorf()` uses float `FPI`, optionally overrides rounding, calls `strtodg`, then packs.
- Handles zero, denormal, normal, infinity, NaN, NaN payload, and sign.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `strtodg` and generated `f_QNAN`.
