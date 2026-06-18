# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat_sigreturn.S

Implements m68k legacy `sigreturn`. It warns for compatibility references and notes that register state must be preserved.

The body uses `trap #1`, which is reserved on m68k for `compat_13_sigreturn13`, then branches to `CERROR` if control returns.

The file also adjusts profiling prologue behavior under `GPROF` so sigreturn does not corrupt user register state.
