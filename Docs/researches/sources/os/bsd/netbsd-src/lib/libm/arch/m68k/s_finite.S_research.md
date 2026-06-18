# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68k/s_finite.S

m68k double `finite` implementation. `_finite` masks the exponent bits and returns false when they equal the all-ones special exponent.
