# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat___sigtramp1.S

Implements the m68k legacy `__sigtramp_sigcontext_1` signal trampoline. The kernel calls the signal handler directly; this trampoline runs only after handler return to invoke old-style signal return.

It computes the `sigcontext` pointer from the stack at `12(%sp)`, places it in the argument slot, uses `trap #3` as the special sigreturn trap, and falls back to `exit` with the returned errno if sigreturn fails.

Filesystem relevance is indirect: this is libc ABI compatibility infrastructure, preserving old NetBSD/m68k binaries that may include filesystem-using programs.
