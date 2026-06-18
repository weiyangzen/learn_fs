# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/sys/ptrace.S

This i386 `ptrace` wrapper clears `errno` via `__errno` before invoking the syscall, allowing callers to distinguish an error from a valid `-1` result. It uses the standard carry/error branch afterward.
