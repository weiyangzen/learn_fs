# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat___sigtramp1.S

Implements SH3 `__sigtramp_sigcontext_1`.

The trampoline is invoked only after signal handler return; it passes `r15` as the sigcontext pointer to `compat_16___sigreturn14`, then exits with errno if sigreturn fails.

This supports old SH signal-delivery ABI.
