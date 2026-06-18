# File Research: sources/os/linux/linux/fs/ceph/metric.h

Defines CephFS client metric IDs, on-wire metric records, aggregate counters, and update helpers.

Key behavior:
- Declares `disable_send_metrics`.
- Enumerates client metric types for caps, read/write/metadata latency, dentry leases, opened files/inodes, pinned caps, I/O sizes, average/stdev variants, and subvolume metrics.
- Defines `CEPHFS_METRIC_SPEC_CLIENT_SUPPORTED`, ordered so the maximum metric bit remains last.
- Defines packed wire structures for each metric item and the metric message head.
- Defines `ceph_subvolume_metric_entry_wire`, the MDS-facing subvolume I/O metric format, plus an older internal tracking struct.
- Defines aggregate metric categories: read, write, metadata, copyfrom, and max.
- Defines `struct ceph_metric` with total count, size sum/min/max, latency sum/avg/squared-sum/min/max, and a spinlock.
- Defines `struct ceph_client_metric` with dentries, caps, operation metrics, opened file/inode counters, selected MDS session, and delayed work.
- Provides `metric_schedule_delayed()`, which schedules one-second delayed work unless metrics sending is disabled.
- Provides inline cap hit/miss increment helpers.
- Provides inline read/write/metadata/copyfrom metric update wrappers around `ceph_update_metrics()`.

Important interactions:
- Used by `metric.c` for encoding/sending and by other CephFS I/O/metadata paths for accounting.
- Embedded in `struct ceph_mds_client` from `mds_client.h`.
