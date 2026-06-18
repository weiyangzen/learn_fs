# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat_sigprocmask.S

Implements MIPS compatibility `sigprocmask`.

It converts the pointer argument to the old integer mask when non-null, substitutes `SIG_BLOCK` when null, calls `compat_13_sigprocmask13`, and stores the returned old mask through the optional output pointer.

Errors tail-call `__cerror`.
