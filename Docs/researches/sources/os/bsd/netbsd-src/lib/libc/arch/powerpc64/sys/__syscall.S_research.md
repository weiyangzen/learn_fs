# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/__syscall.S

This file implements PowerPC64 `__syscall`, `_syscall`, and weak `syscall`. It moves the syscall number into `%r0`, shifts arguments down through `%r10`, loads the final stack argument, executes `sc`, and uses inline error handling on failure.

It is the generic syscall-number entry for PowerPC64. The argument shuffle matches the 64-bit PowerPC calling convention.
