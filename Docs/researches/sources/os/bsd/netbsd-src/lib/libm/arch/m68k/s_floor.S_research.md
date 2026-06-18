# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68k/s_floor.S

m68k `floor` implementation. It saves FPCR, ignores NaN changes, sets round-to-negative-infinity, applies `fintx`, restores FPCR, and returns.
