# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/core.h

`core.h` preserves old core-file constants and, for non-LP64 non-kernel consumers, the obsolete SunOS 4.x a.out `struct core` layout. That structure records register state, executable header, signal, text/data/stack sizes, command name, FPU state, optional SPARC FPU queue, and exception code.

Kernel builds declare `core(int, int)`. Modern consumers should not depend on the old structure.
