# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/pipe.S

AArch64 wrapper for `pipe`.

Key behavior:
- Provides weak `pipe` alias to `_pipe`.
- Saves the caller’s `int fd[2]` pointer in `x9`.
- Calls the kernel `pipe` syscall.
- Stores returned descriptors from `w0` and `w1` into the caller array.
- Returns zero on success.

Dependencies:
- Kernel pipe return convention places two descriptors in return registers.
