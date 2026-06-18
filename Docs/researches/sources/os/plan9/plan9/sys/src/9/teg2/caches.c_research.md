# File Research: sources/os/plan9/plan9/sys/src/9/teg2/caches.c

Cache operation composition layer that exposes all-cache, no-cache, and L1-only `Cacheimpl` vtables.

Key responsibilities:
- Initializes `allcache`, `nocache`, and `l1cache` implementations in `allcacheson`.
- Composes whole-system maintenance by ordering L1 and PL310 L2 operations for invalidate, writeback, and writeback-invalidate.
- Provides range operations used by DMA, page-table, and device code.
- Provides null cache operations for uncached/no-op contexts.
- Provides L1-only vtable wrapping the ARMv7 assembly routines.

Important behavior:
- All combined operations run at `splhi`.
- Writeback-invalidate first writes back L1, then L2, then invalidates/writes back L1 to keep DMA-visible memory coherent.

Dependencies and assumptions:
- Depends on `l2pl310init`, PL310 `l2cache`, and assembly L1 cache helpers.
- Assumes instruction caches are handled elsewhere; this file covers data/unified caches.

Notable risks:
- `cachesoff` only calls `l2cache->off`; L1 remains outside this abstraction.
