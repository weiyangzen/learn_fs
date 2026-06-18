# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/brk.S

This file implements `_brk` with weak public alias `brk`. It clamps the requested break to at least `__minbrk`, invokes the kernel `break` syscall, updates hidden `__curbrk` on success, and returns zero.

It defines `__minbrk` initialized to `_end`; `__curbrk` is declared external/hidden and updated here. The important contract is keeping libc’s tracked program break synchronized with successful kernel changes.
