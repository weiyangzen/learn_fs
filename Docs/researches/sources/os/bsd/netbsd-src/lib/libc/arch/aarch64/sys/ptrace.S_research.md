# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/ptrace.S

AArch64 wrapper for `ptrace`.

Key behavior:
- Saves frame pointer/link register and the first four arguments on the stack.
- Calls `__errno` and clears `errno` before invoking the syscall.
- Restores arguments and stack frame.
- Calls `SYSTRAP(ptrace)`, invokes `__cerror` on error, and returns.

Dependencies:
- `__errno` and NetBSD ptrace syscall semantics.

Notes:
- Clearing `errno` before the syscall supports ptrace requests where `-1` may be a valid data result.
