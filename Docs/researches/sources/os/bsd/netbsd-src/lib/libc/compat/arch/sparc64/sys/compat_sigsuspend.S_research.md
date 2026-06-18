# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat_sigsuspend.S

Implements SPARC64 compatibility `sigsuspend`.

It loads the integer mask from the pointer in `%o0`, invokes `SYS_compat_13_sigsuspend13`, and uses `ERROR()` because the syscall normally returns by interruption.

This is legacy signal-mask compatibility glue.
