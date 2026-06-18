# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat_shmctl.S

Defines the m68k compatibility `shmctl` entry point. It emits a warning directing users to include `<sys/shm.h>` for the correct modern declaration.

The syscall veneer maps `shmctl` to `compat_14_shmctl`.

This is shared-memory ABI compatibility, not filesystem code.
