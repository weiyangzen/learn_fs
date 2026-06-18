# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/__vfork14.S

This file implements PowerPC64 `__vfork14`. After the syscall, it adjusts `%r4` from the kernel parent/child indicator and masks `%r3` so the child returns zero and the parent returns the child PID.

It is minimal vfork return-value glue using PowerPC64 syscall macros.
