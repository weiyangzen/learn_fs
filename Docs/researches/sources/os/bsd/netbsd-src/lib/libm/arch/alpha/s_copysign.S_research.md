# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/alpha/s_copysign.S

Alpha double `copysign`. It uses `cpys fa1, fa0, fv0` to copy the sign of the second argument onto the magnitude of the first, with long-double aliases when applicable.
