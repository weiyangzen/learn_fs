# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/g_xfmt.c

Purpose: Formats an 80-bit extended value stored as five `UShort` words.

Core behavior:
- Defines endian-specific five-word layout.
- Extracts sign, 15-bit exponent, and 64-bit significand.
- Handles zero, infinity, and NaN directly.
- Uses `FPI {64, ...}` and `gdtoa()` for finite values.
- Delegates final printable layout to `g__fmt()`.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `gdtoa`, `g__fmt`, `strcp`, and optional `gdtoa_fltrnds.h`.
