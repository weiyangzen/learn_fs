# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat_sigpending.S

Implements x86_64 compatibility `sigpending`.

After `_SYSCALL(sigpending, compat_13_sigpending13)`, it stores `%eax` into the caller-provided pointer in `%rdi`, clears `%eax`, and returns.

This adapts an old integer mask result to pointer output.
