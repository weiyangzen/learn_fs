# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtodnrp.c

Purpose: Alternate `strtod` implementation for ia32-style extended-precision arithmetic without forcing 53-bit precision control.

Core behavior:
- Parses through `strtodg` using IEEE double `FPI`.
- Packs the returned bits into native double manually.
- Handles no-number, zero, normal, denormal, infinity, NaN, and NaN payload cases.
- On no-memory, sets `errno = ERANGE` and returns a large finite value.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `strtodg`, `Big0`, `Big1`, generated NaN constants, and endian word macros.
