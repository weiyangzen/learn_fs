# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/mremap.S

This file defines the `mremap` syscall wrapper. It performs the standard m68k `SYSCALL(mremap)` sequence and copies the pointer return to `%a0` when building for `__SVR4_ABI__`.

The file contains no extra validation or policy. Its purpose is only architecture-specific syscall and pointer-return ABI glue.
