# File Research: sources/os/linux/linux-stable/fs/ceph/subvolume_metrics.h

## Purpose
Declares the CephFS subvolume metrics data structures and API.

## Main Contents
- `struct ceph_subvol_metric_snapshot`: exported snapshot row containing subvolume ID, read/write ops, byte totals, and latency sums.
- `struct ceph_subvolume_metrics_tracker`: spinlock, cached rb-tree, enable flag, entry count, debug counters, and cumulative read/write totals.
- Function prototypes for lifecycle, enable/disable, record, snapshot, dump, I/O wrapper, and slab-cache lifecycle.
- Inline `ceph_subvolume_metrics_enabled()` using `READ_ONCE()`.

## Integration Points
Included by CephFS MDS/client and debugfs code. The tracker is embedded in `struct ceph_mds_client`, while the implementation records I/O using `struct ceph_inode_info`.

## Risks And Review Focus
- `enabled` is a fast-path lockless read; callers that need tree consistency must still use implementation locking.
- The snapshot structure exposes latency sums, not averages; consumers must divide by operation counts.
