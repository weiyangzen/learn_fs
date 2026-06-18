# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/seed48.c

Implements `seed48(unsigned short xseed[3])`. It saves the current global `__rand48_seed` in a static three-word buffer, installs the caller’s seed, resets multiplier/addend constants, and returns the saved seed pointer.

The returned buffer is static and overwritten by subsequent `seed48()` calls.
