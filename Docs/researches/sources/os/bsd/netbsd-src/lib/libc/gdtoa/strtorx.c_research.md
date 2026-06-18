# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtorx.c

Purpose: Parses with an explicit rounding mode into five-`UShort` 80-bit extended storage.

Core behavior:
- Defines endian-specific five-word layout.
- `ULtox()` packs result bits into exponent/integer/significand words.
- `strtorx()` uses `FPI {64, ...}`, optionally overrides rounding, calls `strtodg`, then packs.
- Handles zero, denormal, normal, infinity, NaN, NaN payload, and sign.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `strtodg` and generated `ldus_QNAN*` constants.
