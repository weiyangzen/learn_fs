# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat_sigprocmask.S

Implements x86_64 compatibility `sigprocmask`.

It checks whether `%rsi` (`set`) is null, substitutes `SIG_BLOCK` when null, otherwise loads `*set` into `%esi`, calls `compat_13_sigprocmask13`, and optionally stores the returned old mask through `%rdx`.

Errors jump to `CERROR`, with PIC handling.
