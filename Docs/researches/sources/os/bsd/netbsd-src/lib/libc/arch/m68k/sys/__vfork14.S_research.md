# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/__vfork14.S

This file implements the m68k `__vfork14` wrapper. Because parent and child temporarily share the stack, it removes the return address before the syscall and later jumps to it instead of using a normal `rts`.

On success it converts the kernel’s parent/child indicator in `%d1` into standard `vfork` return semantics: parent gets child PID, child gets zero. On error it stores errno through either `__errno` or global `errno`, returns `-1`, and jumps back to the saved return address.
