# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/map.h

Purpose: Declares legacy kernel resource-map allocation routines.

Key APIs:
- `rmallocmap()`, `rmallocmap_wait()`, `rmfreemap()`
- `rmalloc()`, `rmalloc_wait()`, `rmfree()`

Important detail: The public type is opaque (`struct map` forward declaration); callers use map handles through the allocation/free routines.

Relevance to subset A: Kernel memory/resource allocation utility that may be used by low-level subsystems.
