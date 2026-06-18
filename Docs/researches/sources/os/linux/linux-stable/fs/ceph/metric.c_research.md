# File Research: sources/os/linux/linux-stable/fs/ceph/metric.c

## Purpose

`metric.c` collects and periodically sends CephFS client metrics to an MDS session that supports metric collection. It serializes cap, lease, inode/file, latency, I/O size, metadata, and optional subvolume metrics into `CEPH_MSG_CLIENT_METRICS` messages.

## Major Responsibilities

- Computes encoded lengths for subvolume metrics and serializes subvolume metric snapshots in the MDS-compatible wire format.
- Converts kernel `ktime_t` values to Ceph wire `ceph_timespec`.
- Builds metrics messages containing:
  - cap hit/miss/total counts,
  - read latency,
  - write latency,
  - metadata latency,
  - dentry lease hit/miss/total counts,
  - opened files,
  - pinned icaps,
  - opened inodes,
  - read I/O operation and byte totals,
  - write I/O operation and byte totals,
  - optional subvolume metrics.
- Sends metrics only when the selected MDS rank is active.
- Snapshots subvolume metrics only when both local tracking is enabled and the session advertises `CEPHFS_FEATURE_SUBVOLUME_METRICS`.
- Maintains `mdsc->subvol_metrics_last`, sent counters, and nonzero send counters after successful subvolume metric transmission.
- Finds a suitable metric session by scanning open client sessions that support `CEPHFS_FEATURE_METRIC_COLLECT`.
- Runs delayed metric work once per second unless sending is disabled or the client is stopping.
- Initializes/destroys percpu counters, atomics, metric accumulators, session refs, and delayed work.
- Updates metric totals, min/max, average, and variance-like square sum in `ceph_update_metrics()`.

## Important Behavior

- The worker avoids sending metrics to sessions lacking support because older MDSes may close the socket on unknown metric messages.
- If subvolume metrics are enabled, the worker skips sessions that do not support the subvolume metric feature rather than sending a partially unsupported payload.
- `disable_send_metrics` prevents scheduling and causes the worker to emit a one-time informational message.
- `ceph_update_metrics()` ignores most negative return codes, but counts `-ENOENT` and `-ETIMEDOUT` along with successful operations.

## Concurrency and Lifetime Notes

- Metric counters use atomics, percpu counters, and per-metric spinlocks.
- The delayed worker holds and releases session references through `mdsc->metric.session`.
- Subvolume last-sent snapshot state is protected by `subvol_metrics_last_mutex`.
- Destroy cancels delayed work before tearing down counters and dropping the stored session reference.

## Research Notes

This file is a telemetry adjunct to the MDS client rather than a correctness path for metadata operations. Its compatibility gates are important: metric sending is session-feature negotiated, and subvolume metrics have an additional feature gate.
