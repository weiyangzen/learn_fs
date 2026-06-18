# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_fmod.S

i387 double `fmod` implementation. It loops on `fprem` until the x87 C2 status bit clears, drops the divisor from the FP stack, and returns the remainder.
