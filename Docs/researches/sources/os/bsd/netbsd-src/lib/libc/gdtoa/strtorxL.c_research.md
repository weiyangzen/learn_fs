# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtorxL.c

Purpose: Parses with an explicit rounding mode into three-`ULong` 80-bit extended storage.

Core behavior:
- Defines endian-specific three-word layout.
- `ULtoxL()` packs result bits into exponent/significand words.
- `strtorxL()` uses `FPI {64, ...}`, optionally overrides rounding, calls `strtodg`, then packs.
- Handles zero, normal, denormal, infinity, NaN, NaN payload, and sign.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `strtodg` and generated `ld_QNAN*` constants.
