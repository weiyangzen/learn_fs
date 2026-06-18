# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/lcong48.c

Read completely: 43 lines.

Implements `lcong48(unsigned short p[7])`. It copies three seed words, three multiplier words, and the additive constant from the caller array into the global rand48 generator state.

This reconfigures subsequent global-state rand48 calls.
