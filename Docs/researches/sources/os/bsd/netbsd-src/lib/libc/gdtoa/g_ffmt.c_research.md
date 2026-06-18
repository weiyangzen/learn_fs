# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/g_ffmt.c

Purpose: Formats a native IEEE float into a general decimal string.

Core behavior:
- Extracts sign, exponent, and 24-bit significand from one `ULong`.
- Handles zero, infinity, and NaN directly.
- Uses `FPI {24, ...}` and `gdtoa()` for finite values.
- Requires extra buffer space for shortest-mode float output.
- Delegates final decimal/exponent layout to `g__fmt()`.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `gdtoa`, `g__fmt`, `strcp`, and optional `gdtoa_fltrnds.h`.
