# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat_sigpending13.S

Implements PowerPC compatibility `sigpending`.

It saves the output pointer in `r5`, calls `compat_13_sigpending13`, stores the returned mask into `*r5`, returns zero on success, and branches to `__cerror` on syscall failure.

This adapts old integer signal masks to the pointer API.
