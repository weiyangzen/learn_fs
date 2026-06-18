# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/metaslab_impl.h

This private header defines the in-core state for the ZFS metaslab allocator: allocation tracing records, weight encoding, metaslab classes, metaslab groups, individual metaslabs, and the on-disk unflushed-TXG side record.

Core definitions:
- `metaslab_alloc_trace_t` records allocator attempts, selected group/metaslab, request size, weight, DVA, offset, and allocator index; `trace_alloc_type_t` reserves negative offset values for allocator failure reasons.
- Weight macros divide the 64-bit metaslab weight into active bits, space-vs-segment mode, histogram bucket index, and segment count.
- `metaslab_class` groups vdev allocation classes, owns allocator ops, rotor, allocation throttle state, class-wide space/histogram counters, and selected-TXG multilist.
- `metaslab_group` models a top-level vdev allocation domain with primary/secondary active metaslabs, AVL weight tree, allocation eligibility, queue-depth throttle counters, fragmentation/histogram summaries, and disabled-metaslab coordination.
- `metaslab` owns the per-metaslab locks, space map, alloc/free/defer/checkpoint/trim range trees, loaded/flushing/condensing flags, histograms, weights, active allocator state, auxiliary size-sorted btrees, unflushed log-spacemap trees, and sync-length tracking.

Important invariants:
- `ms_lock` serializes allocator/free paths with sync-side state; `ms_sync_lock` coordinates space-map writers and removal readers.
- Loaded and unloaded metaslabs compute weight from different data sources, so `ms_synchist` and `ms_deferhist` preserve exact spacemap histogram entries without range-tree consolidation drift.
- `ms_allocatable_by_size` must mirror `ms_allocatable` segment membership with a different ordering.
- `ms_unflushed_txg` means changes at that TXG and later live in log spacemaps, not the metaslab spacemap.
- Condensing, flushing, loading, disabling, and allocation activation are all explicit state-machine fields; callers must respect their lock and CV protocols.
