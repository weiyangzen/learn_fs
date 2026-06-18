# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtorQ.c

Purpose: Parses with an explicit rounding mode into quad-precision storage.

Core behavior:
- `ULtoQ()` packs `strtodg` bits and result class into quad storage.
- `strtorQ()` copies the default quad `FPI` and overrides `rounding` when requested.
- Handles zero, denormal, normal, infinity, NaN, NaN payload, and sign.
- Returns the `STRTOG_*` parse flags.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `strtodg`, generated `ld_QNAN*` constants, and endian word macros.
