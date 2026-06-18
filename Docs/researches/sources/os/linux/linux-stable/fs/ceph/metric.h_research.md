# File Research: sources/os/linux/linux-stable/fs/ceph/metric.h

## Purpose

`metric.h` defines CephFS client metric types, supported metric bitsets, on-wire metric structures, internal metric counters, and inline update helpers.

## Major Definitions

- `enum ceph_metric_type` enumerates supported metric payload types, including cap info, read/write/metadata latency, dentry lease stats, opened files/inodes, pinned icaps, read/write I/O sizes, average/stdev metric identifiers, and subvolume metrics.
- `CEPHFS_METRIC_SPEC_CLIENT_SUPPORTED` lists metric types advertised during session open.
- `struct ceph_metric_header` is the common packed header for most metric records.
- Packed wire records define cap, latency, lease, opened file, pinned icap, opened inode, and read/write I/O size payloads.
- `struct ceph_subvolume_metric_entry_wire` defines the MDS-compatible subvolume metrics wire layout with 32-bit clamped operation counts and 64-bit byte/latency fields.
- `struct ceph_metric` stores internal totals, size min/max/sum, latency min/max/sum/average/square sum, protected by a spinlock.
- `struct ceph_client_metric` stores global dentry, cap, file, inode, and operation metrics plus the metric session and delayed work.

## Inline Helpers

- `metric_schedule_delayed()` schedules per-second metric work unless metrics sending is disabled.
- `ceph_update_cap_hit()` and `ceph_update_cap_mis()` update cap counters.
- `ceph_update_read_metrics()`, `ceph_update_write_metrics()`, `ceph_update_metadata_metrics()`, and `ceph_update_copyfrom_metrics()` dispatch to `ceph_update_metrics()` with the correct internal metric bucket.

## Research Notes

This header defines the metric wire contract used by `metric.c` and the feature-advertised metric spec encoded by `mds_client.c`. Any wire layout change must remain consistent with the MDS side, especially `ceph_subvolume_metric_entry_wire`.
