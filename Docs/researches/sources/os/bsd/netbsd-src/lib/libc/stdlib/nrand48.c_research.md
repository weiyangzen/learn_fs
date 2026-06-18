# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/nrand48.c

Implements `nrand48(unsigned short xseed[3])`. It advances the caller-provided 48-bit seed array and returns a non-negative 31-bit result from the updated high seed words.

The function asserts a non-NULL seed pointer and does not touch the global `__rand48_seed`.
