# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat_sigpending.S

Implements SPARC64 compatibility `sigpending`.

It saves the output pointer in `%o2`, invokes `SYS_compat_13_sigpending13`, stores the returned mask into `*%o2` on success, and returns zero.

Failures enter `ERROR()`.
