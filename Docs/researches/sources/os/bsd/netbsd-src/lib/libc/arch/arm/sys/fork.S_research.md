# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/fork.S

This ARM `__fork` wrapper invokes the `fork` syscall and uses the kernel's `r1` parent/child indicator to return the child pid in the parent and zero in the child.
