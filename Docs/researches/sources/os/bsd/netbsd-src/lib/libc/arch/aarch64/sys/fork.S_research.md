# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/fork.S

AArch64 wrapper for `__fork`.

Key behavior:
- Uses `_SYSCALL(__fork, fork)` to call the kernel `fork`.
- Converts fork-style return registers so the child gets return value zero and the parent keeps child pid.
- Returns to caller.

Dependencies:
- Kernel fork return convention: `x1` parent/child discriminator.
