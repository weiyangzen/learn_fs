# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat___sigtramp1.S

Implements the SPARC `__sigtramp_sigcontext_1` legacy signal trampoline.

It documents the signal stack layout, saves global registers and `%y`, conditionally saves FPU state when enabled, calls the handler through `%g1`, restores saved state, then invokes `compat_16___sigreturn14`. If sigreturn fails, it calls `exit`.

This is one of the more complex files in the group because SPARC register windows and FPU state require careful trampoline preservation.
