# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat_sigpending13.S

Implements VAX compatibility `sigpending`.

After `_SYSCALL(sigpending, compat_13_sigpending13)`, it stores `%r0` through the pointer at `4(%ap)`, clears `%r0`, and returns.

This adapts the old integer mask result to the pointer output API.
