# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/g_Qfmt.c

Purpose: Formats a 128-bit IEEE-style quad value into a general decimal string.

Core behavior:
- Defines endian-specific word order for four `ULong` words.
- Extracts sign, exponent, and 113-bit significand bits.
- Handles zero, infinity, and NaN directly.
- Uses `FPI {113, ...}` and `gdtoa()` for finite numbers.
- Uses mode 0 when `ndig <= 0`, otherwise mode 2 for requested significant digits.
- Passes the generated digit string to `g__fmt()` for final decimal/exponent formatting.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `gdtoa`, `g__fmt`, `strcp`, and optional `gdtoa_fltrnds.h`.
