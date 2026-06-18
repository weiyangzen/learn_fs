# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/fork.S

This HPPA `__fork` wrapper invokes `fork` and normalizes the kernel's second return register so the child returns zero while the parent returns the child pid.
