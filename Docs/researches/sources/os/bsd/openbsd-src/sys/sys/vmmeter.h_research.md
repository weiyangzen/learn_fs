# File Research: sources/os/bsd/openbsd-src/sys/sys/vmmeter.h

Defines system-wide VM and fork accounting structures. `struct vmtotal` records run queue, disk/page wait, sleeping/swapped runnable counts, virtual/real memory totals, shared memory counts, and free pages.

`struct forkstat` records counts and affected page totals for `fork`, `vfork`, `__tfork`, and kernel threads. The file also defines sysctl ids and names for fork stats.
