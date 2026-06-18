# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/__syscall.S

This file implements or1k `__syscall`, `_syscall`, and weak `syscall`. It takes the syscall number from `r3`, shifts up to five register arguments down into the kernel’s expected registers, loads additional arguments from the stack into `r8`, `r11`, and `r12`, executes `l.sys 0`, and branches to `__cerror` on failure.

The file is the generic syscall-number entry point. Its argument shuffling is the main semantic content.
