# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_logbl.S

i387 long-double `logbl`. It loads the long double argument, extracts exponent with `fxtract`, discards the significand, and returns.
