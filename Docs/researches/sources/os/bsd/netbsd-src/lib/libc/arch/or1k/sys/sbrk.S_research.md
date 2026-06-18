# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/sbrk.S

This file implements `_sbrk` with weak alias `sbrk`. It loads hidden `__curbrk`, adds the requested increment, calls the kernel `break` syscall, updates `__curbrk` with the new break, and returns the old break in `r11`.

It has PIC and non-PIC symbol-address paths. It is paired with `brk.S` and relies on updating cached break state only after successful syscalls.
