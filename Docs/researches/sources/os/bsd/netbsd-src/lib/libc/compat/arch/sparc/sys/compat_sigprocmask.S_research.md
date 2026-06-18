# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat_sigprocmask.S

Implements SPARC compatibility `sigprocmask`.

It dereferences `set` into `%o1` when non-null, otherwise uses `SIG_BLOCK`, invokes `SYS_compat_13_sigprocmask13`, and optionally stores the returned old mask into `*oset`.

This adapts modern pointer arguments to the old integer mask syscall.
