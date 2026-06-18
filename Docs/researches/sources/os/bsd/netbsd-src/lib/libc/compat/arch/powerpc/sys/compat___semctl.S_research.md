# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat___semctl.S

Defines PowerPC compatibility `__semctl`.

It maps `__semctl` to `compat_14___semctl` using the syscall `PSEUDO` macro.

This is System V semaphore ABI compatibility.
