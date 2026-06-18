# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/SYS.h

This m68k syscall header defines `SYSTRAP` as loading the syscall number into `%d0` and executing `trap #0`. Wrapper macros branch to hidden `__cerror` on carry and provide pseudo, no-error, raw, and weak syscall variants.
