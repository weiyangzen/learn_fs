# File Research: sources/os/bsd/freebsd-src/sys/sys/ktr_class.h

Defines the bitmask classes used by KTR tracing. Classes include general, network, device, lock, SMP, subsystem, pmap, malloc, trap, interrupt, signal, process, syscall, init, eventhandler, VFS/VOP, VM, IPv4/IPv6, run queue, UMA, callout, GEOM, busdma, scheduler, buffer cache, and ptrace.

`KTR_ALL` enables all 32 bits. `KTR_COMPILE` defaults to all classes when `KTR` is defined and zero otherwise, controlling compile-time trace elision.
