# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/g_ddfmt.c

Purpose: Formats a double-double value held as two `double`s.

Core behavior:
- Handles NaN, infinity, signed zero, and infinity-minus-infinity cases.
- Orders the two components by magnitude, converts each to `Bigint`, aligns exponents, then sums or subtracts.
- Normalizes trailing zero bits before formatting.
- Chooses an `FPI` width based on the computed significand, with a minimum of 106 bits.
- Uses `gdtoa()` and `g__fmt()` for final output.

Dependencies:
- Includes `gdtoaimp.h` and `string.h`.
- Uses `d2b`, `lshift`, `diff`, `sum`, `rshift`, `lo0bits`, `hi0bits`, `gdtoa`, and `Bfree`.
