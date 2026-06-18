# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat_sigsuspend.S

Implements SH3 compatibility `sigsuspend`.

It loads the integer signal mask from `@r4`, invokes `SYS_compat_13_sigsuspend13`, returns zero only on unexpected success, and jumps to `CERROR` on normal error/interrupt.

This is old signal-mask ABI glue.
