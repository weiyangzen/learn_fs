# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/__vfork14.S

This file implements PowerPC `__vfork14`. After the syscall, it adjusts `%r4` from the kernel parent/child flag and masks `%r3` so the child returns zero while the parent returns the child PID.

It is minimal vfork return-value adaptation. Error handling is provided by the `SYSCALL` macro.
