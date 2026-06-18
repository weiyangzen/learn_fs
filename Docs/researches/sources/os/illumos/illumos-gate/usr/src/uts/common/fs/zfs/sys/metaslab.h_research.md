# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/metaslab.h

Read status: complete, 142 lines.

Purpose: metaslab allocation/free/class/group interface for SPA space allocation.

Key structures and APIs:
- `metaslab_ops_t` contains the allocation strategy callback `msop_alloc`.
- Global `zfs_metaslab_ops` points to active allocation operations.
- Per-metaslab APIs cover init/fini, unflushed TXG and estimated condensed size state, sorting by flushed status, memory used by unflushed changes, load/unload/flush, allocated-space query, sync/sync_done/reassess, and largest allocatable extent.
- Allocation flags include hint favor/avoid, gang header/child, async allocation, no throttle, must reserve, and fastwrite.
- Allocation/free/claim APIs include `metaslab_alloc()`, `metaslab_alloc_dva()`, `metaslab_free()`, `metaslab_free_concrete()`, `metaslab_free_dva()`, `metaslab_free_impl_cb()`, `metaslab_unalloc_dva()`, `metaslab_claim()`, `metaslab_claim_impl()`, and `metaslab_check_free()`.
- Stats/trace APIs initialize/finalize metaslab stats and allocation trace lists.
- Class APIs create/destroy/validate classes, verify histograms, report fragmentation/expandable/allocated/space/dspace/deferred values, throttle reserve/unreserve, and evict old metaslabs.
- Group APIs create/destroy/activate/passivate groups, check initialized state, query space/fragmentation, verify/remove histograms, decrement/verify allocation, recalculate weight/sort metaslabs, disable/enable metaslabs, and set selected TXG.
- `metaslab_space_update()` adjusts vdev/class space accounting.

Dependencies: SPA, space map, TXG, ZIO, AVL.

Research notes:
- This is the allocator-facing API that SPA/ZIO use to reserve, allocate, free, claim, and account DVAs.
- `metaslab_debug_load` is exported as a debug control.
