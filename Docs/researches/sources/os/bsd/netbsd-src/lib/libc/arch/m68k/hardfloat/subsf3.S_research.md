# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/subsf3.S

m68k hardfloat `__subsf3`.

Key points:
- Loads first float into `%fp0`.
- Subtracts second float with `fsubs`.
- Returns float result for non-SVR4 ABI.
