# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_fmod.S

mc68881 double `__ieee754_fmod` implementation. It loads the dividend, applies `fmodd` with the divisor, and returns the double remainder.
