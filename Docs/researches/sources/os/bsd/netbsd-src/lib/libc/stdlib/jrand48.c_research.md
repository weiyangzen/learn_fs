# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/jrand48.c

Read completely: 39 lines.

Implements `jrand48(unsigned short xseed[3])`. It advances the caller-provided seed and returns a signed 32-bit-style value formed from the high seed word sign-extended through `int16_t` and the middle seed word.

It does not use the global seed, unlike `lrand48()`/`drand48()`.
