# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_scalbnf.S

x86 float `scalbnf`, `scalblnf`, and `ldexpf`. It uses `fild`, `flds`, and `fscale`, with separate 32-bit and 64-bit exponent entry points on x86-64.
