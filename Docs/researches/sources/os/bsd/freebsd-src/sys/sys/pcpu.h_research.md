# File Research: sources/os/bsd/freebsd-src/sys/sys/pcpu.h

This header defines machine-independent per-CPU state and dynamic per-CPU data access. It refuses assembler inclusion, includes core lock/cpuset/resource/queue headers plus machine-specific `pcpu.h`, and is mostly kernel-facing.

Dynamic per-CPU data is represented by linker set boundaries `__start_set_pcpu`/`__stop_set_pcpu`, an offset array `dpcpu_off[]`, and macros for defining, declaring, and accessing per-CPU variables. `DPCPU_GET`, `SET`, `PTR`, `ID_*`, `SUM`, `VARSUM`, and `ZERO` abstract access to current and remote CPU copies. Some module/architecture combinations avoid `static` definitions because PC-relative loads may not get relocations suitable for KLD per-CPU allocation.

`struct pcpu` records core per-CPU runtime state: current/idle/fp/dead threads, current PCB, scheduler state, context-switch timing, CPU id, all-CPU linkage, spinlock list, CPU state ticks, device handle, netisr state, VFS free vnode hint, memory domain, rmlock queue, dynamic per-CPU base, early counter, zpcpu offset, and machine-dependent fields kept last for offset stability.

The zpcpu helpers provide access to UMA per-CPU allocations with protected set/add/sub operations, CPU-specific offset translation hooks, and replacement helpers. The header also declares CPU/per-CPU initialization, lookup, allocation, copy, free, and debug display hooks. Filesystem relevance includes per-CPU counters, VFS free vnode accounting, UMA per-CPU allocation patterns, and synchronization-sensitive kernel performance.
