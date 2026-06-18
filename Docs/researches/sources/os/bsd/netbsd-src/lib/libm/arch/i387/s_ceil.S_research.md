# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_ceil.S

x86 double `ceil`. It saves the x87 control word, sets rounding toward positive infinity, executes `frndint`, restores the original control word, and returns via x87 or SSE ABI handling.
