# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat___sigtramp1.S

Implements MIPS `__sigtramp_sigcontext_1`.

The kernel calls the handler directly; the trampoline takes the `sigcontext` at `sp`, passes it to `compat_16___sigreturn14`, and exits with errno if sigreturn fails.

This is architecture-specific legacy signal ABI support.
