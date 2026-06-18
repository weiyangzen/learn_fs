# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/pipe.S

Alpha wrapper for `pipe`.

Key behavior:
- Provides weak `pipe` alias to `_pipe`.
- Calls kernel `pipe`.
- Stores returned descriptors from `v0` and `a4` into the caller’s `int fd[2]` array.
- Returns zero on success.

Dependencies:
- Alpha pipe syscall convention returning two descriptors in registers.
