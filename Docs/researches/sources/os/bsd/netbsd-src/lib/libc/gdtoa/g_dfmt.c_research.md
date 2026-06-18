# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/g_dfmt.c

Purpose: Formats a native IEEE double into a general decimal string.

Core behavior:
- Extracts sign, exponent, and 53-bit significand from two `ULong` words.
- Handles zero, infinity, and NaN directly.
- Converts finite values through `gdtoa()` with an IEEE double `FPI`.
- Uses shortest mode when `ndig <= 0`, otherwise requested significant digits.
- Sends the result through `g__fmt()`.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `gdtoa`, `g__fmt`, `strcp`, and optional `gdtoa_fltrnds.h`.
