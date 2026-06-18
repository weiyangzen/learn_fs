# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat_Ovfork.S

Implements PowerPC legacy `vfork`.

After the syscall, it adjusts `r4` from the kernel parent/child indicator and masks `r3` so the child returns zero and the parent returns the child pid.

This preserves old process-control ABI behavior.
