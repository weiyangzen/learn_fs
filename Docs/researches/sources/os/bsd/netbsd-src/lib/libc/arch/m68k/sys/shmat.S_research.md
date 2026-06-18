# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/shmat.S

This file defines the `shmat` syscall wrapper. It performs the standard m68k syscall sequence and, for SVR4 ABI builds, mirrors the returned attached address into `%a0`.

The wrapper contains no local validation. Its role is preserving pointer-return ABI details for System V shared memory attachment.
