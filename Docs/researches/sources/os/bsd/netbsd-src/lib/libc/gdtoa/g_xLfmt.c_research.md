# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/g_xLfmt.c

Purpose: Formats an 80-bit extended value stored in three `ULong` words.

Core behavior:
- Defines endian-specific word layout.
- Extracts sign, 15-bit exponent, and 64-bit significand.
- Handles zero, infinity, and NaN directly.
- Uses `FPI {64, ...}` and `gdtoa()` for finite values.
- Emits shortest or requested-significant-digit output through `g__fmt()`.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `gdtoa`, `g__fmt`, `strcp`, and optional `gdtoa_fltrnds.h`.
