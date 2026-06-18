# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/erand48_ieee754.c

Read completely: 47 lines.

IEEE-754-specific `erand48()` implementation. It advances the seed, constructs an IEEE double with exponent bias for `[1, 2)`, fills fraction bits from the 48-bit random state, and subtracts `1` to return `[0, 1)`.

This avoids arithmetic `ldexp()` construction but depends on `<machine/ieee.h>` layout.
