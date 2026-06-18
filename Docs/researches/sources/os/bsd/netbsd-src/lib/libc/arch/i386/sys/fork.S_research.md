# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/fork.S

This i386 `__fork` wrapper invokes `fork` and normalizes the kernel's `%edx` parent/child indicator so the parent receives the child pid and the child receives zero.
