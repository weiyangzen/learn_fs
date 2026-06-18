# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/cerror.S

AArch64 common syscall error handler.

Key behavior:
- Saves `x19` and `x30`.
- Preserves the kernel error number from `w0` in `w19`.
- Calls `__errno`, stores the error number through the returned pointer, restores registers, and returns `-1`.

Dependencies:
- Reentrant libc `__errno`.
- Syscall stubs branch here on error.
