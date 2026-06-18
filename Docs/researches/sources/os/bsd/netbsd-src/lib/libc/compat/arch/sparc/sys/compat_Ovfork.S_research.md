# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat_Ovfork.S

Implements SPARC compatibility `vfork`.

It uses the kernel-provided `%o1` parent/child indicator, decrements it, and masks `%o0` so child returns zero while parent returns the child pid.

This is old process-control ABI compatibility.
