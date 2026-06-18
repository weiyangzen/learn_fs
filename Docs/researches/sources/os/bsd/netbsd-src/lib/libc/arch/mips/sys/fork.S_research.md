# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/fork.S

This file implements MIPS `__fork`. It issues the `fork` syscall, branches to `__cerror` if `a3` indicates failure, and uses `v1` to distinguish parent from child.

On child return it sets `v0` to zero; in the parent it leaves the child PID in `v0`. This is standard fork ABI adaptation for MIPS libc.
