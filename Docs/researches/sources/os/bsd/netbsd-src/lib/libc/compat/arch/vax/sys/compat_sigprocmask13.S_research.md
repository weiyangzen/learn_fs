# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat_sigprocmask13.S

Implements VAX compatibility `sigprocmask`.

It dereferences the new mask pointer when non-null, substitutes `SIG_BLOCK` when null, invokes `SYS_compat_13_sigprocmask13`, and optionally stores the returned old mask through the output pointer.

Errors jump to `CERROR+2`.
