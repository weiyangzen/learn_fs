# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/lrand48.c

Read completely: 33 lines.

Implements `lrand48()`. It advances the global rand48 seed and returns a nonnegative long built from the high 31 bits of the updated 48-bit state.

The expression uses `seed[2] * 32768 + (seed[1] >> 1)`.
