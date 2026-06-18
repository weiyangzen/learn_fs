# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/syscall.S

AArch64 public `syscall` wrapper.

Key behavior:
- Defines `FUNCNAME` as `_syscall`.
- Defines `SYSTRAP_SYSCALL` as `SYSTRAP(syscall)`.
- Includes `__syscall.S` to instantiate the generic wrapper for the `syscall` kernel entry.
- Provides weak alias `syscall` to `_syscall`.

Dependencies:
- `__syscall.S` macro-parameterized implementation.
