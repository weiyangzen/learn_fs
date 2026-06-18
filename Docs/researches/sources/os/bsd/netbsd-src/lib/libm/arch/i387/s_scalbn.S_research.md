# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_scalbn.S

x86 double `scalbn`, `scalbln`, and `ldexp` implementation. It loads an integer exponent onto the x87 stack, scales the double with `fscale`, cleans up the FP stack, and returns.
