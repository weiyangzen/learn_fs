# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_sysfs.c

Implements XFS sysfs attribute types and kobject trees for global stats/debug state, per-mount stats, log state, metadata IO error policy, and zoned filesystem state.

Generic sysfs machinery:
- `struct xfs_sysfs_attr` wraps a kernel `attribute` with XFS-specific show/store callbacks.
- `xfs_sysfs_object_show` and `xfs_sysfs_object_store` dispatch from sysfs ops to the wrapped callbacks.
- `xfs_mp_ktype` is the base per-mount kobject type.

Debug sysfs attributes under `DEBUG`:
- `bug_on_assert`
- `log_recovery_delay`
- `mount_delay`
- `always_cow`
- `pwork_threads`
- `larp`
- `bload_leaf_slack`
- `bload_node_slack`
These mutate or display fields in `xfs_globals`. Validation is local to each store handler, such as delay limits of 0-60 seconds and pwork thread limits from `-1` to `num_possible_cpus()`.

Stats sysfs:
- `stats_show` calls `xfs_stats_format`.
- `stats_clear_store` accepts only value `1` and calls `xfs_stats_clearall`.
- `xfs_stats_ktype` exposes `stats` and `stats_clear`.

Log sysfs:
- Converts a kobject to `struct xlog`.
- Exposes:
  - `log_head_lsn`
  - `log_tail_lsn`
  - `reserve_grant_head_bytes`
  - `write_grant_head_bytes`
- The log head read is protected by `l_icloglock`; tail and grant heads use existing atomic/log helpers.

Metadata error configuration:
- Sysfs layout is `.../xfs/<dev>/error/<class>/<errno>/<attrs>`.
- `max_retries` accepts `-1` for forever or nonnegative retry counts.
- `retry_timeout_seconds` accepts `-1` for forever or 0-86400 seconds.
- `fail_at_unmount` is stored on `struct xfs_mount`.
- `xfs_error_meta_init` defines defaults for metadata `default`, `EIO`, `ENOSPC`, and `ENODEV`.
- `xfs_error_sysfs_init_class` creates errno child kobjects and initializes retry policy, unwinding already-created entries on failure.
- `xfs_error_get_cfg` maps runtime errno values to the configured metadata error policy slot.

Zoned sysfs:
- For zoned realtime filesystems, exposes:
  - `max_open_zones`, adjusted to exclude GC-reserved zones
  - `nr_open_zones`
  - `zonegc_low_space`
- Changing `zonegc_low_space` validates 0-100 and wakes zone GC if the value changes.

Per-mount sysfs lifecycle:
- `xfs_mount_sysfs_init` creates:
  - `.../xfs/<dev>/`
  - `stats/`
  - `error/`
  - `error/fail_at_unmount`
  - `error/metadata/...`
  - optional `zoned/`
- `xfs_mount_sysfs_del` removes optional zoned state, error cfg kobjects, metadata/error dirs, stats dir, and mount dir.

Research notes:
- The file is the bridge between runtime XFS internals and user-visible sysfs control/inspection.
- Attribute handlers generally parse with `kstrto*` helpers and return `-EINVAL` for out-of-range values.
- `xfs_mount_sysfs_del` assumes kobject lifecycle helpers tolerate the initialized mount layout; changes to created error classes must keep deletion order in sync.
