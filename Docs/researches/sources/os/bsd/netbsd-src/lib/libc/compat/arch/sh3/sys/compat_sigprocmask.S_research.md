# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat_sigprocmask.S

Implements SH3 compatibility `sigprocmask`.

It tests whether `set` is null, substitutes `SIG_BLOCK` for null masks, otherwise loads `*set`, invokes `SYS_compat_13_sigprocmask13`, and optionally stores the returned old mask to `*oset`.

Errors jump to `CERROR`.
