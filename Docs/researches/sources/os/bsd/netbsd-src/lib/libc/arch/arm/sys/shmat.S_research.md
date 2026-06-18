# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/shmat.S

This file defines the ARM `shmat` syscall wrapper using `RSYSCALL(shmat)`. All trap and error behavior is inherited from `SYS.h`.

It is a thin libc syscall stub with no local argument reshaping.
