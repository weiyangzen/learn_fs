# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/fork.S

This IA-64 `__fork` wrapper invokes `fork` through `CALLSYS_ERROR` and returns. A comment notes child return-value handling is still incomplete.
