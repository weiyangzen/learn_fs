# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_floor.S

x86 double `floor`. It saves the x87 control word, sets rounding toward negative infinity, runs `frndint`, restores control, and returns.
