# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/string/bzero.S

This file implements MIPS `bzero`. It handles small lengths bytewise, aligns the destination to register width, clears whole words using `REG_S`, then clears trailing bytes.

For 32-bit register builds it uses `SWHI` to clear initial unaligned bytes; for 64-bit it constructs masks to partially clear an unaligned word. Correctness depends on `SZREG`, endian-specific mask direction, and avoiding writes outside the requested range.
