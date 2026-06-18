# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat___sigtramp2.S

Implements VAX `__sigtramp_sigcontext_2`.

The trampoline saves scratch registers, calls the handler with `callg (%ap),(%fp)`, restores registers, adjusts `ap` to point at the sigcontext argument, invokes `compat_16___sigreturn14`, and halts if control returns.

This is a VAX-specific legacy signal trampoline.
