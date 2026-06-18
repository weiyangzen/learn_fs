# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat___sigtramp1.S

Implements the SPARC64 `__sigtramp_sigcontext_1` legacy signal trampoline.

It documents the 64-bit signal stack layout, saves global registers, checks dirty FPU register state with `%fprs`, saves/restores FPU blocks using block load/store ASIs, preserves `%y`, calls the handler via `%g1`, then invokes `compat_16___sigreturn14`. If sigreturn fails, it exits.

This is architecture-specific compatibility code with careful register-window and floating-point preservation.
