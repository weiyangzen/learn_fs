# File Research: sources/os/linux/linux/fs/ceph/subvolume_metrics.h

Public interface for CephFS per-subvolume metrics.

Defines:
- `struct ceph_subvol_metric_snapshot`: point-in-time counters for a subvolume: ID, read/write ops, read/write bytes, cumulative read/write latency.
- `struct ceph_subvolume_metrics_tracker`: spinlock, cached rb-tree root, entry count, enabled flag, debug counters, and cumulative total read/write counters.

Declared APIs:
- Tracker lifecycle: `ceph_subvolume_metrics_init()`, `_destroy()`, `_enable()`.
- Recording: `ceph_subvolume_metrics_record()` and inode/MDS-aware `ceph_subvolume_metrics_record_io()`.
- Snapshotting: `ceph_subvolume_metrics_snapshot()` and `_free_snapshot()`.
- Debug output: `ceph_subvolume_metrics_dump()`.
- Slab lifecycle: `ceph_subvolume_metrics_cache_init()` and `_destroy()`.

Inline helper:
- `ceph_subvolume_metrics_enabled()` uses `READ_ONCE(tracker->enabled)` for lockless enabled checks.

Role in subsystem:
- Included by Ceph super/client setup and metrics paths.
- Uses forward declarations for `seq_file`, `ceph_mds_client`, and `ceph_inode_info` to avoid broad header coupling.
