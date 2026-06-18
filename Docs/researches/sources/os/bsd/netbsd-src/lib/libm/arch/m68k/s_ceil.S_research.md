# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68k/s_ceil.S

m68k `ceil` implementation. It saves FPCR, loads the double argument, returns NaN unchanged, sets round-to-positive-infinity, applies `fintx`, restores FPCR, and returns.
