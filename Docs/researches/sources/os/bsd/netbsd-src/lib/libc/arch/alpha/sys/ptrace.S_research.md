# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/ptrace.S

Alpha wrapper for `ptrace`.

Key behavior:
- Sets up GP.
- Clears global `errno` before calling the syscall.
- Calls `ptrace` through common error handling and returns.

Dependencies:
- Alpha syscall macros and errno storage.

Notes:
- Clearing `errno` before ptrace supports callers distinguishing a valid `-1` return from an error.
