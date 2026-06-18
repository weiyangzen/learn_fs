# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat_sigsuspend.S

Implements x86_64 compatibility `sigsuspend`.

It loads the integer signal mask from `(%rdi)`, invokes `compat_13_sigsuspend13`, returns zero only on unexpected success, and jumps to `CERROR` on error, with PIC handling.

This bridges pointer-style libc calls to the old signal-mask syscall.
