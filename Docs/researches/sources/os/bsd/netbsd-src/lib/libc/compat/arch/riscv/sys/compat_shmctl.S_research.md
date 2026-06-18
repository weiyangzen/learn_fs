# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/compat_shmctl.S

Defines RISC-V compatibility `shmctl`.

It warns callers to include `<sys/shm.h>` and maps to `compat_14_shmctl`.

This is a simple shared-memory compatibility veneer.
