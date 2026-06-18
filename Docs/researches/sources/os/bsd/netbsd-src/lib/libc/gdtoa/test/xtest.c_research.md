# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/xtest.c

Test driver for 80-bit extended format represented as five 16-bit words: `g_xfmt`, `strtoIx`, `strtopx`, and `strtorx`.

Behavior:
- Reads rounding, digit count, raw half-word hex representation, or decimal input.
- Uses endian-specific `_0.._4` word indexes.
- For nearest rounding, checks `strtorx` against `strtopx`.
- Tests interval results from `strtoIx`.
- Prints host `long double` only when `sizeof(long double) == 12`.

Dependencies: `gdtoa.h`, `getround`, extended-format conversion helpers.
