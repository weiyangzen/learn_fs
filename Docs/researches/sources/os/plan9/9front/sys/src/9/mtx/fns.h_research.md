# File Research: sources/os/plan9/9front/sys/src/9/mtx/fns.h

This header declares MTX platform functions and macros used across C and assembly-backed code. It includes portable function declarations, MMU/cache helpers, interrupt controller APIs, I/O port functions, PCI config accessors, process FP hooks, Raven/MPIC functions, timer stubs, trap entry, TLB flushes, and address translation macros.

Important macros include `coherence()` as `eieio()`, no-op `cycles`, no-op `idlehands`, no-op `kmapinval`, `userureg`, `KADDR`, and `PADDR`.

Filesystem relevance is dependency-level: most platform source files include this header, and page faults, device files, PCI drivers, and console/network drivers rely on these declarations.

Notable risks: several operations are macros or stubs on this port, so code shared from other architectures may assume stronger behavior than MTX provides.
