# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/sbrk.S

This file implements `_sbrk` with weak public alias `sbrk`. It defines hidden `__curbrk` initialized to `_end`, adds the requested increment to the current break, calls the kernel `break` syscall, updates `__curbrk` on success, and returns the old break.

It is tightly coupled to `brk.S` through shared program-break state. Overflow and address validity are left to arithmetic/kernel behavior; libc’s responsibility here is maintaining the cached break on successful calls.
