# File Research: sources/os/linux/linux-stable/fs/ceph/subvolume_metrics.c

## Purpose
Implements per-subvolume CephFS I/O metrics collection, snapshotting, debugfs dumping, and slab-cache lifecycle for metric rb-tree entries.

## Main Interfaces
- Tracker lifecycle: `ceph_subvolume_metrics_init()`, `ceph_subvolume_metrics_destroy()`, `ceph_subvolume_metrics_enable()`.
- Recording: `ceph_subvolume_metrics_record()`, `ceph_subvolume_metrics_record_io()`.
- Snapshot/reporting: `ceph_subvolume_metrics_snapshot()`, `ceph_subvolume_metrics_free_snapshot()`, `ceph_subvolume_metrics_dump()`.
- Cache lifecycle: `ceph_subvolume_metrics_cache_init()`, `ceph_subvolume_metrics_cache_destroy()`.

## Control Flow
Metrics are stored in a cached rb-tree keyed by subvolume ID. Recording skips disabled trackers, unknown subvolume ID `0`, zero-size operations, and zero latency. On a miss, the code drops the spinlock, allocates a new entry from `ceph_subvol_metric_entry_cachep`, then retries under lock to handle concurrent insertion. Read/write operation counts, byte totals, and latency sums are updated per entry, while cumulative tracker totals are atomics.

`snapshot()` first counts active entries under lock, allocates an array, then walks the tree again to copy active entries into `ceph_subvol_metric_snapshot` records. With `consume=true`, copied entries are reset and removed. Entries with no activity are pruned during snapshot walking. `dump()` formats current active entries directly to a `seq_file`.

## State And Synchronization
`tracker->lock` protects the rb-tree and `nr_entries`; `enabled` is read with `READ_ONCE()` and rechecked under lock. Debug counters and cumulative totals use `atomic64_t`.

## Integration Points
`ceph_subvolume_metrics_record_io()` links the tracker to CephFS I/O paths by reading `ci->i_subvolume_id`, measuring elapsed `ktime`, and dispatching read/write activity into `mdsc->subvol_metrics`.

## Risks And Review Focus
- Allocation outside the spinlock is correct but relies on retry/free paths staying balanced.
- Snapshot count and copy are separated, so races are handled by truncating to the allocated count and warning.
- Locking around `seq_printf()` keeps output consistent but can hold the spinlock while formatting many entries.
