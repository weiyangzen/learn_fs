# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_ilogbl.S

i387 long-double `ilogbl`. It uses `fxtract` to split significand/exponent, discards the significand, stores the exponent as an integer, and returns it in `%eax`.
