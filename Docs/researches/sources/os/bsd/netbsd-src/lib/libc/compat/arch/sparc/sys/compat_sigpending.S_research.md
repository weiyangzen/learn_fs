# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat_sigpending.S

Implements SPARC compatibility `sigpending`.

It saves the output pointer in `%o2`, invokes `SYS_compat_13_sigpending13`, stores the returned mask through the saved pointer on success, and returns zero.

On failure it enters the standard `ERROR()` path.
