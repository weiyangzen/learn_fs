# File Research: sources/os/linux/linux/fs/ceph/metric.c

Implements CephFS client metric collection, encoding, delayed sending, and latency/stat aggregation.

Key behavior:
- Encodes subvolume metric snapshots in a versioned on-wire format compatible with the MDS/FUSE client expectation, with operation counts clamped to u32 and byte/latency counters preserved as u64.
- Sends `CEPH_MSG_CLIENT_METRICS` only to active MDS sessions that advertise metric collection support.
- Includes metrics for cap hits/misses/total caps, read latency, write latency, metadata latency, dentry lease hits/misses, opened files, pinned icaps, opened inodes, read I/O sizes, and write I/O sizes.
- Optionally includes subvolume metrics when the local tracker is enabled and the target session supports `CEPHFS_FEATURE_SUBVOLUME_METRICS`.
- Saves the last sent subvolume metric snapshot and send counters under `subvol_metrics_last_mutex`.
- Finds an eligible MDS session for metric sending, skipping sessions without metric support and skipping non-subvolume-capable sessions when subvolume metrics are enabled.
- Delayed metric work exits during MDS client stopping, respects the global `disable_send_metrics` module parameter, warns if no eligible session exists, and reschedules once per second.
- Initializes percpu counters, atomic counters, per-metric locks, min/max/average/stdev accumulator fields, and delayed work.
- Destroys delayed work and all percpu counters, and drops the held metric session reference.
- Updates metric aggregates for successful operations and selected negative results (`-ENOENT`, `-ETIMEDOUT`) using running mean and squared-sum variance accumulation.

Important interactions:
- Bound to an MDS session by `mds_client.c` when session open features include metric collection.
- Uses `struct ceph_client_metric` and wire structs from `metric.h`.
- Reads total caps, dentry/inode counters, and operation latency data maintained by other CephFS paths.
- Integrates subvolume metrics through `subvolume_metrics` tracker helpers.
