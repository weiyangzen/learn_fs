# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/xLtest.c

Test driver for extended long-double format using three `ULong` words: `g_xLfmt`, `strtoIxL`, `strtopxL`, and `strtorxL`.

Behavior:
- Handles rounding mode, output digit count, raw hex words, and decimal inputs.
- Uses endian-specific `_0.._2` word ordering.
- For nearest rounding, compares `strtorxL` with `strtopxL`.
- Tests interval conversion through `strtoIxL`.
- If `sizeof(long double) == 12`, prints `%.21Lg` for host-readable output.

Dependencies: `gdtoa.h`, `getround`, extended long-double gdtoa helpers.
