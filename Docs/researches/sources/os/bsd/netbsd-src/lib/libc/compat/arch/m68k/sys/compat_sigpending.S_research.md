# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat_sigpending.S

Implements m68k compatibility `sigpending` around `compat_13_sigpending13`. It includes old SCCS/RCS metadata and emits a warning for direct compatibility references.

After `_SYSCALL`, it stores the returned old integer signal mask through the caller-provided pointer at `4(%sp)`, clears `%d0`, and returns success.

This adapts the legacy integer-mask syscall result to the libc pointer-return API expected by old callers.
