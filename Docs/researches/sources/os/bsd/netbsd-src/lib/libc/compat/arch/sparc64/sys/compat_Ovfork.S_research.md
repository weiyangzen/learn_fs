# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat_Ovfork.S

Implements SPARC64 compatibility `vfork`.

It decrements `%o1` and masks `%o0` to produce zero in the child and child pid in the parent.

This is old process-control ABI compatibility.
