# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/string/bcmp.S

This file implements `bcmp(s1, s2, n)` for MIPS. It quickly handles small byte counts, aligns when possible, compares aligned words in a loop, and has an unaligned path using endian-aware `LWHI`/`LWLO` partial-word loads.

It returns zero for equality and one for mismatch. The implementation is performance-oriented but depends on careful address alignment, byte-order macros, and MIPS branch-delay-slot scheduling.
