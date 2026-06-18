# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_acos.S

mc68881 double `__ieee754_acos` implementation. It uses the FPU `facosd` instruction and returns the result through `d0:d1`.
