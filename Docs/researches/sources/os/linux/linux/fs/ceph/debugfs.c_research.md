# File Research: sources/os/linux/linux/fs/ceph/debugfs.c

## Role

`debugfs.c` provides CephFS client debugfs files when `CONFIG_DEBUG_FS` is enabled. It is a read-mostly inspection layer over the mounted filesystem client, MDS client, sessions, caps, request tree, and metrics. With debugfs disabled, `ceph_fs_debugfs_init()` and `ceph_fs_debugfs_cleanup()` compile to empty stubs.

## Main Interfaces

- `ceph_fs_debugfs_init(struct ceph_fs_client *fsc)` creates debugfs entries under `fsc->client->debugfs_dir`.
- `ceph_fs_debugfs_cleanup(struct ceph_fs_client *fsc)` removes those entries.
- `DEFINE_SHOW_ATTRIBUTE(...)` exports seq_file show handlers for `mdsmap`, `mdsc`, `caps`, `mds_sessions`, `status`, metric files, `metric_features`, and `subvolumes`.
- `congestion_kb_fops` is a writable simple attribute for `mount_options->congestion_kb`.

## Debugfs Tree

Created entries include:

- `writeback_congestion_kb`: read/write mount writeback congestion threshold.
- `bdi`: symlink to the backing device info debugfs entry.
- `mdsmap`: current MDS map epoch/root/max/session timings/rank address/state.
- `mds_sessions`: client global id, mount name, and active MDS session states.
- `mdsc`: in-flight MDS requests, operation names, unsafe state, and involved paths/inodes.
- `caps`: cap reservation status, per-session inode cap issuance, and cap waiters.
- `status`: client entity instance/address/nonce and blocklisted state.
- `metrics/file`, `metrics/latency`, `metrics/size`, `metrics/caps`, `metrics/metric_features`, `metrics/subvolumes`.

## Data and Control Flow

- `mdsmap_show()` reads `fsc->mdsc->mdsmap` and dumps core map fields plus rank state names from `ceph_mds_state_name()`.
- `mdsc_show()` locks `mdsc->mutex`, walks `mdsc->request_tree`, formats request tids, sessions, ops, unsafe status, and primary/secondary target paths. It uses `ceph_mdsc_build_path()` for dentries and frees path info after printing.
- Metric show functions snapshot counters and per-metric spinlock-protected fields:
  - `metrics_file_show()` reports inode/file/cap counters.
  - `metrics_latency_show()` prints total/average/min/max/stdev for read/write/metadata/copyfrom.
  - `metrics_size_show()` prints size totals for operations that have byte metrics, skipping metadata.
  - `metrics_caps_show()` reports dentry lease and inode cap hit/miss counters.
- `caps_show()` reports global cap reservation counts, then iterates MDS sessions and each session's caps with `ceph_iterate_session_caps()`. It also prints `mdsc->cap_wait_list`.
- `subvolume_metrics_show()` copies the last sent subvolume snapshot under `subvol_metrics_last_mutex`, prints it outside the mutex, then dumps pending metrics through `ceph_subvolume_metrics_dump()`.
- `metric_features_show()` snapshots the metric session feature bitset under `mdsc->mutex`, then explains whether client metrics and subvolume metrics are effectively enabled.

## Concurrency and Lifetime

- `mdsc->mutex` protects request tree and session table walks.
- Session-specific cap iteration is done by dropping `mdsc->mutex`, taking `session->s_mutex`, iterating, then reacquiring `mdsc->mutex`.
- Per-inode cap display takes `ci->i_ceph_lock`.
- Metric arrays use each metric's spinlock for coherent totals.
- Subvolume last-sent snapshots are duplicated with `kmemdup_array()` so formatting does not hold the mutex.
- Cleanup removes individual entries and recursively removes `debugfs_metrics_dir`; removal is tolerant of missing entries.

## Dependencies

This file depends on CephFS internal structures from `super.h`, `mds_client.h`, `metric.h`, and `subvolume_metrics.h`, plus libceph debugfs/auth/mon helpers. It does not implement filesystem behavior; it exposes runtime state maintained by directory, file, MDS, capability, and metric code.

## Error Handling and Edge Cases

- Missing `mdsc` or `mdsmap` yields empty or explanatory output, not errors.
- Failed path construction in request dumps is printed as an empty string.
- Failed subvolume snapshot allocation simply reports no last-sent entries while still printing counters and pending metrics.
- Min latency/size sentinels (`KTIME_MAX`, `U64_MAX`) are rendered as zero.
