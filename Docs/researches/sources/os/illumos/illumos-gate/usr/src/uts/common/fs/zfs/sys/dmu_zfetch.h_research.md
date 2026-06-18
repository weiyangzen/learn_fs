# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dmu_zfetch.h

Read status: complete, 81 lines.

Purpose: DMU sequential-read prefetch tracking interface.

Key structures and APIs:
- `zfetch_t` owns a read/write lock, list of streams, owning dnode, and stream count.
- `zstream_t` tracks expected next block id, next prefetched block id, next indirect-prefetch block id, lock, timing, list linkage, parent fetch, and pending block refcount.
- Global tunable extern: `zfetch_array_rd_sz`.
- Lifecycle APIs: `zfetch_init()`, `zfetch_fini()`, `dmu_zfetch_init()`, `dmu_zfetch_fini()`.
- `dmu_zfetch()` observes accesses and may issue data/metadata prefetch.

Dependencies: ZFS context, dnode forward declaration, refcounts.

Research notes:
- Tightly connected to dnode access and dbuf prefetch, but isolated behind a small state structure embedded in `dnode_t`.
