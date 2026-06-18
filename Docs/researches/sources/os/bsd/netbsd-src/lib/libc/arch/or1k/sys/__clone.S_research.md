# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/__clone.S

This file implements or1k `__clone` and weak `clone`. It checks that function and stack arguments are non-NULL, saves the function pointer, rearranges arguments for the kernel `__clone(flags, stack)` syscall, and branches to `__cerror` on invalid input or syscall error.

The parent returns normally; the child calls the saved function with the supplied argument and then calls `_exit`. PIC builds set up the GOT before calling `_exit`, since that path does not return.
