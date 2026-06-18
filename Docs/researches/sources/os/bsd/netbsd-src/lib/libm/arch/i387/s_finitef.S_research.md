# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_finitef.S

x86 float `finitef` implementation. `_finitef` masks the float exponent field and returns true when it is not the all-ones special exponent.
