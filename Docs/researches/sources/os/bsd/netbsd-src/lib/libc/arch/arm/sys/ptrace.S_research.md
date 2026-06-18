# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/ptrace.S

This ARM `ptrace` wrapper clears `errno` before issuing the syscall so a legitimate `-1` result can be distinguished by callers. It handles both reentrant `__errno` and global `errno` cases, then uses normal syscall error handling.
