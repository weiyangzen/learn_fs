# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/mulsf3.S

m68k hardfloat `__mulsf3`.

Key points:
- Loads first float into `%fp0`.
- Multiplies by second float with `fmuls`.
- Returns float result for non-SVR4 ABI.
