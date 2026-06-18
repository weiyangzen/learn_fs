# File Research: sources/os/plan9/9front/sys/src/9/teg2/caches.c

Defines cache-operation composition layers. `allcaches` combines L1 architectural operations with external L2 operations in the correct order for invalidate, writeback, and writeback+invalidate, both whole-cache and range-based. `nullcaches` is a no-op implementation, and `l1caches` wraps only L1 operations.

`allcacheson` initializes PL310 and sets global `allcache`, `nocache`, and `l1cache` pointers. DMA-sensitive paths rely on this wrapper so data reaches RAM before device reads and stale CPU cachelines are invalidated after device writes.
