# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/__syscall.S

This file builds `__syscall` with the generic `RSYSCALL` macro from m68k `SYS.h`. It supplies the internal variadic syscall entry point used for direct syscall-number based calls.

Its behavior is inherited from the macro definitions: perform the trap, branch to `CERROR` on carry/error, and return syscall results otherwise.
