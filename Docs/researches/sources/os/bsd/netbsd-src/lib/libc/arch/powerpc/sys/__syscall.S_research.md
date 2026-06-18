# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/__syscall.S

This file implements PowerPC `__syscall`, `_syscall`, and weak `syscall`. It moves the caller-supplied syscall number from `%r3` to `%r0`, shifts register arguments down, loads the final stack argument, executes `sc`, and branches to error handling if summary overflow is set.

It is the generic syscall-number entry for PowerPC. The argument shifting is the key ABI-specific behavior.
