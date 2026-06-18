# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat_sigsuspend.S

Implements SPARC compatibility `sigsuspend`.

It loads the integer mask from the pointer in `%o0`, invokes `SYS_compat_13_sigsuspend13`, and uses `ERROR()` because the syscall normally returns through interruption.

This is legacy signal-mask compatibility.
