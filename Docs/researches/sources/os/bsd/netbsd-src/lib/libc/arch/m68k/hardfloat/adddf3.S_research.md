# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/adddf3.S

This m68k FPU helper implements `__adddf3` for double addition using `fmoved` and `faddd`. For non-SVR4 ABI builds it moves the double result back through `%d0/%d1`.
