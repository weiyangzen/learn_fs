# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/Makefile.inc

This make include configures OpenRISC/or1k libc architecture sources. It adds `__sigtramp2.S` and `mulsi3.S`, includes the architecture directory, and generates `sysassym.h` from installed syscall headers using `syscallargs.awk` and `genassym`.

`sysassym.h` supplies syscall argument counts used by `SYS.h` to load stack arguments for syscalls with more than six register arguments. SoftFloat support is conditionally included when enabled.
