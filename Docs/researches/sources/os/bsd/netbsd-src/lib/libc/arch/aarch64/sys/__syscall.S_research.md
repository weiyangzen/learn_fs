# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/__syscall.S

Generic AArch64 syscall-number dispatch wrapper.

Key behavior:
- Defines `FUNCNAME` as `__syscall` and syscall trap as `SYSTRAP(__syscall)` unless overridden.
- Rejects builds with `SYS_MAXSYSARGS > 8`.
- Moves the syscall number from `x0` to `x17`.
- Shifts arguments down from `x1..x7` into `x0..x6`.
- Loads the eighth syscall argument from the stack into `x7`.
- Traps, invokes `__cerror` on failure, and returns.

Dependencies:
- AArch64 calling convention and NetBSD syscall argument convention.
- Reused by `syscall.S` with different macro definitions.
