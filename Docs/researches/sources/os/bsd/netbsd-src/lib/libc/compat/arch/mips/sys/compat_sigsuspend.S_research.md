# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat_sigsuspend.S

Implements MIPS compatibility `sigsuspend`.

It loads the legacy integer mask from the pointer in `a0`, invokes `compat_13_sigsuspend13`, returns zero only on unexpected success, and tail-calls `__cerror` on normal interrupt/error paths.

This adapts pointer-style libc calls to the old signal-mask syscall.
