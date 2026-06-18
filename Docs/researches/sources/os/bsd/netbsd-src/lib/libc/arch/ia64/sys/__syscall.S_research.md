# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/ia64/sys/__syscall.S

This IA-64 file includes `SYS.h` and defines `__syscall` via `RSYSCALL(__syscall)`. It uses the standard macro path for trap and error behavior.

It is a thin wrapper for the special libc `__syscall` entry.
