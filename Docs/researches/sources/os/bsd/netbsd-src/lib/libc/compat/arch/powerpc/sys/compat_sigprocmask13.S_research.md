# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat_sigprocmask13.S

Implements PowerPC compatibility `sigprocmask`.

If `set` is non-null it loads `*set` into the syscall argument; if null it uses `SIG_BLOCK`. It calls `compat_13_sigprocmask13`, optionally stores the returned old mask into `*oset`, and returns zero.

Errors branch to `__cerror`.
