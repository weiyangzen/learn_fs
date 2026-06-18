# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/sbrk.S

This file implements `_sbrk` with weak alias `sbrk`. It defines `__curbrk` initialized to `_end`, adds the requested increment to the cached break, calls the kernel `break` syscall, stores the new break on success, and returns the old break.

It is paired with `brk.S` through shared `__curbrk` state. Correctness depends on preserving the old value while issuing the syscall and updating only after success.
