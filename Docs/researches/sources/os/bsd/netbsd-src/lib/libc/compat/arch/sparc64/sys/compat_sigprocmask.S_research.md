# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat_sigprocmask.S

Implements SPARC64 compatibility `sigprocmask`.

It dereferences a non-null `set` pointer into `%o1`, otherwise sets `%o0` to `SIG_BLOCK`, invokes `SYS_compat_13_sigprocmask13`, and optionally stores the returned old mask through `oset`.

This adapts pointer-style libc arguments to the old integer mask syscall.
