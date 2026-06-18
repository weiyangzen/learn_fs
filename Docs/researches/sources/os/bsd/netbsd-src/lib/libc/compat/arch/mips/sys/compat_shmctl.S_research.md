# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat_shmctl.S

Defines MIPS compatibility `shmctl`.

It warns callers to include `<sys/shm.h>` and routes to `compat_14_shmctl`.

This is shared-memory compatibility glue.
