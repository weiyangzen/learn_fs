# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtord.c

Purpose: Parses with an explicit rounding mode into double storage.

Core behavior:
- `ULtod()` packs `strtodg` bits and result class into IEEE double words.
- `strtord()` uses double `FPI` and overrides `rounding` when requested.
- Handles zero, denormal, normal, infinity, NaN, NaN payload, and sign.
- Locale is passed through to `strtodg`.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `strtodg`, generated double NaN constants, and endian word macros.
