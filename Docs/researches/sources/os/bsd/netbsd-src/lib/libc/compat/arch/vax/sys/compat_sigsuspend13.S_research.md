# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat_sigsuspend13.S

Implements VAX compatibility `sigsuspend`.

It dereferences the signal-mask pointer into the syscall argument, invokes `compat_13_sigsuspend13`, and returns zero only on unexpected success; errors jump to `CERROR+2`.

This bridges pointer-style libc calls to the old integer-mask syscall.
