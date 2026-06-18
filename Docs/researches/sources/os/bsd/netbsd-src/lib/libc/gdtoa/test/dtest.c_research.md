# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/dtest.c

Test program for ordinary double gdtoa entry points: `g_dfmt`, `strtoId`, `strtod`, `strtopd`, and `strtord`.

Behavior:
- Reads rounding changes, digit-count changes, raw two-word hex doubles, or decimal inputs.
- For nearest rounding, compares `strtord` with both libc `strtod` and `strtopd`.
- Formats the result through `g_dfmt`.
- Uses `strtoId` to produce lower/upper interval bounds and reports their relation to the rounded result.

Dependencies: `gdtoaimp.h`, `getround`, double conversion/format helpers.
