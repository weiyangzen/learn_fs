# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtodI.c

Purpose: Parses a string into a two-double interval bracketing the exact value.

Core behavior:
- Uses double `FPI` with `strtodg`.
- Packs the rounded result into `dd[0]`.
- Uses `STRTOG_Inexlo`/`STRTOG_Inexhi` to decide whether to set the other endpoint to the next higher or lower double.
- Handles sign by reversing inexact direction.
- Handles zero, denormal, normal, infinity, NaN, and NaN payload cases.
- Uses `ulpdown()` to step downward across exponent-boundary cases correctly.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `strtodg`, `ulp`, generated NaN constants, and word-level double access macros.
