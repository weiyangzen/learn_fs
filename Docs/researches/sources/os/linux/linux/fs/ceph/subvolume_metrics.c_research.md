# File Research: sources/os/linux/linux/fs/ceph/subvolume_metrics.c

Implements per-subvolume CephFS I/O metrics tracking. Metrics are stored in an rb-tree keyed by subvolume ID and can be snapshotted, consumed, dumped through debugfs, and recorded from timed read/write operations.

Key structures:
- Internal `ceph_subvol_metric_rb_entry`: rb-node plus read/write operation counts, byte counts, and cumulative latencies.
- Global `ceph_subvol_metric_entry_cachep`: kmem cache for rb entries.
- Public tracker fields are defined in `subvolume_metrics.h`.

Main APIs:
- `ceph_subvolume_metrics_init()`: initializes spinlock, cached rb root, enabled flag, and atomic counters.
- `ceph_subvolume_metrics_destroy()`: clears all entries and disables collection.
- `ceph_subvolume_metrics_enable()`: toggles collection; disabling clears the rb-tree.
- `ceph_subvolume_metrics_record()`: records one read/write sample for a subvolume.
- `ceph_subvolume_metrics_snapshot()`: returns an allocated array of active entries, optionally consuming/resetting tree state.
- `ceph_subvolume_metrics_free_snapshot()`: frees snapshot arrays.
- `ceph_subvolume_metrics_dump()`: prints current entries and average latencies to a seq_file.
- `ceph_subvolume_metrics_record_io()`: wrapper that extracts inode subvolume ID and computes elapsed microseconds.
- `ceph_subvolume_metrics_cache_init()` / `_destroy()`: kmem cache lifecycle.

Concurrency:
- Tree and `nr_entries` are protected by `tracker->lock`.
- Debug/accounting counters use `atomic64_t`.
- `record()` uses a two-pass allocation pattern: check under lock, allocate outside lock, then retry/insert, freeing raced allocations if another thread inserted first.

Filtering:
- Recording skips disabled tracker, subvolume ID 0 (`CEPH_SUBVOLUME_ID_NONE`), zero size, or zero latency.
- `record_io()` increments counters for calls, disabled state, and missing subvolume IDs.
- Negative/zero measured latency is coerced to 1 microsecond before record.

Snapshot behavior:
- Counts active entries first, allocates an array, then copies under lock.
- With `consume=true`, entries are erased and freed after copy.
- Entries with no activity are pruned.
