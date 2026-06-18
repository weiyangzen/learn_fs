# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/callo.h

`callo.h` is the private kernel header for callout/timeout scheduling. It defines `callout_t`, the 64-bit internal callout id layout, flags, generation/counter/table partitioning, short/long-term ID spaces, realtime/normal table types, hash sizes, heap layout, and callout-list flags.

It also defines locality-aware callout caches, hash/list/heap/table structures, kstat counters, heap sizing policy, and constants for TCP resolution, alignment, maximum ticks, and tolerance. Kernel exports initialize callouts, handle CPU online/offline, react to hrestime changes, and provide `membar_sync`.
