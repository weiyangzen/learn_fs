# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/srand48.c

Implements `srand48(long seed)`. It sets the low seed word to the fixed `RAND48_SEED_0`, fills the upper two seed words from the 32-bit seed value, and resets the standard multiplier and addend.

This reinitializes the global `rand48` sequence.
