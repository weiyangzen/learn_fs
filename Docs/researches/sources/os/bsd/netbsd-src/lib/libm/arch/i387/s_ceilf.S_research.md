# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_ceilf.S

x86 float `ceilf`. It temporarily sets x87 rounding to positive infinity, rounds with `frndint`, restores the control word, and returns a float.
