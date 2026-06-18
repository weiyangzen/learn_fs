# File Research: sources/os/linux/linux-stable/fs/ceph/debugfs.c

## Purpose

`debugfs.c` exposes CephFS client state through Linux debugfs when `CONFIG_DEBUG_FS` is enabled. It provides read-only diagnostic views for MDS maps, outstanding MDS requests, capability state, MDS sessions, client status, general metrics, negotiated feature bits, and subvolume metrics, plus a writable debugfs knob for writeback congestion.

## Main Responsibilities

- Creates and removes CephFS debugfs files under the Ceph client debugfs directory.
- Dumps current MDS map information.
- Dumps in-flight MDS client requests and their path/inode context.
- Dumps capability pool status, per-session caps, and cap waiters.
- Dumps MDS session identities and states.
- Dumps client instance and blocklist status.
- Dumps metric counters, latency distributions, size distributions, and cap/dentry cache hit/miss counters.
- Dumps subvolume metric snapshots and pending metric state.
- Shows negotiated MDS session feature bits relevant to metric collection.
- Exposes `writeback_congestion_kb` as a simple writable debugfs attribute.

## Debugfs Entries

Top-level files created by `ceph_fs_debugfs_init()`:
- `writeback_congestion_kb`: read/write mount option for writeback congestion threshold.
- `bdi`: symlink to the backing device info debugfs directory.
- `mdsmap`: MDS map epoch, root, max rank, timeouts, and rank addresses/states.
- `mds_sessions`: client identity and active MDS session states.
- `mdsc`: outstanding MDS requests.
- `caps`: capability pool and per-inode cap table.
- `status`: messenger entity instance and blocklist status.
- `metrics/`: metric subdirectory.

Metric files:
- `metrics/file`: total inodes, opened files, pinned caps, opened inodes.
- `metrics/latency`: read/write/metadata/copyfrom operation latency totals, averages, min/max, and stdev.
- `metrics/size`: read/write/copyfrom size totals, averages, min/max, and summed bytes.
- `metrics/caps`: dentry lease and inode cap hit/miss counters.
- `metrics/metric_features`: session feature-bit report and metrics enablement decision.
- `metrics/subvolumes`: last sent and pending subvolume I/O metrics.

## Locking and Data Access

- MDS request and session trees are walked under `mdsc->mutex`.
- Per-session capability iteration takes `session->s_mutex`.
- Individual inode cap state is read under `ci->i_ceph_lock`.
- Cap waiters are read under `mdsc->caps_list_lock`.
- Metric latency and size structures use per-metric spinlocks.
- Subvolume metric snapshots are copied under `subvol_metrics_last_mutex` before formatting, avoiding long seq_file output while holding the mutex.

## Notable Formatting Helpers

- `CEPH_LAT_METRIC_SHOW` converts ktime values to microseconds and derives a standard deviation-like display value from the stored squared latency sum.
- `CEPH_SZ_METRIC_SHOW` normalizes an unset `U64_MAX` minimum to zero for display.
- `ceph_session_feature_table` maps CephFS feature bits to stable debugfs names for `metric_features_show()`.

## Disabled Build Behavior

When `CONFIG_DEBUG_FS` is not enabled:
- `ceph_fs_debugfs_init()` is an empty function.
- `ceph_fs_debugfs_cleanup()` is an empty function.
- None of the seq_file/debugfs helpers are compiled.

## Important Dependencies

- `mds_client.h`: request trees, sessions, caps, feature bits, request path helpers.
- `metric.h`: client metric counters and latency/size state.
- `subvolume_metrics.h`: pending and last-sent subvolume metrics.
- Ceph common debugfs support from `linux/ceph/debugfs.h`.
- Linux `seq_file`, debugfs, atomics, percpu counters, and ktime helpers.

## Edge Cases and Risks

- `mdsc_show()` builds paths for dentries while holding request iteration state; it carefully releases path metadata with `ceph_mdsc_free_path_info()`.
- `metric_features_show()` reports disabled metrics if there is no current metric session or if the MDS session lacks `METRIC_COLLECT`.
- Subvolume metric snapshot allocation can fail; the output then reports no last-sent entries but still prints aggregate send counters and pending metrics.
- Cleanup uses individual `debugfs_remove()` calls plus `debugfs_remove_recursive()` for the metrics directory; debugfs tolerates missing entries.
