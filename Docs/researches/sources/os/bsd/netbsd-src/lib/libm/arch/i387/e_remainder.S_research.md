# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_remainder.S

i387 double IEEE remainder implementation. It loops on `fprem1` until the x87 C2 status bit clears, then returns the computed remainder.
