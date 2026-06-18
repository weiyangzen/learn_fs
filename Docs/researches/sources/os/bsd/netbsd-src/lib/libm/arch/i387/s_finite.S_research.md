# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_finite.S

x86 double `finite`. It masks exponent bits and returns true when they are not all ones, using stack words on i386 and `%xmm0` spill/mask on x86-64.
