# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/__syscall.S

This HPPA file includes `SYS.h` and defines `__syscall` via `RSYSCALL(__syscall)`. It relies entirely on the HPPA syscall macro layer for trap and error handling.

It is a thin wrapper for the special libc `__syscall` entry point.
