# File Research: sources/os/linux/linux/fs/xfs/xfs_sysfs.c

## Purpose

`xfs_sysfs.c` implements XFS sysfs objects and attributes for global stats, per-mount stats, log state, metadata I/O error handling policy, debug knobs, and zoned realtime status.

## Generic Sysfs Layer

- `struct xfs_sysfs_attr` wraps `struct attribute` with XFS-specific show/store callbacks.
- `XFS_SYSFS_ATTR_RW`, `XFS_SYSFS_ATTR_RO`, and `XFS_SYSFS_ATTR_WO` define typed attributes.
- `xfs_sysfs_object_show` and `xfs_sysfs_object_store` dispatch generic sysfs operations to the XFS attribute callbacks.
- `xfs_sysfs_ops` is reused by the kobject types in this file.
- `xfs_mp_ktype` defines the per-mount root object type. It currently has no default mount-root attributes.

## Debug Sysfs Attributes

Compiled under `DEBUG`:

- `bug_on_assert`: toggles `xfs_globals.bug_on_assert`.
- `log_recovery_delay`: integer delay from 0 to 60 seconds.
- `mount_delay`: integer mount delay from 0 to 60 seconds.
- `always_cow`: bool forcing COW behavior for reflink debug testing.
- `pwork_threads`: parallel workqueue thread override from -1 to `num_possible_cpus()`.
- `larp`: logged attribute recovery persistence testing knob.
- `bload_leaf_slack` and `bload_node_slack`: btree bulk load slack controls.
- `xfs_dbg_ktype`: global debug kobject type for these attributes.

## Stats Sysfs Attributes

- `to_xstats` maps the stats kobject to `struct xstats`.
- `stats_show` calls `xfs_stats_format`.
- `stats_clear_store` accepts only value `1` and clears the associated stats object with `xfs_stats_clearall`.
- `xfs_stats_ktype` provides `stats` and `stats_clear` attributes for global and per-mount stats directories.

## Log Sysfs Attributes

- `to_xlog` maps the kobject to `struct xlog`.
- `log_head_lsn` reads current cycle/block under `l_icloglock`.
- `log_tail_lsn` cracks the atomic tail LSN.
- `reserve_grant_head_bytes` and `write_grant_head_bytes` expose grant head byte counters.
- `xfs_log_ktype` groups these log attributes.

## Metadata Error Policy Sysfs

- Directory shape is `.../xfs/<dev>/error/<class>/<errno>/<error_attrs>`.
- `to_error_cfg` maps errno-level kobjects to `struct xfs_error_cfg`.
- `err_to_mp` maps the error root kobject to the mount.
- `max_retries` exposes retry count, mapping `XFS_ERR_RETRY_FOREVER` to `-1`.
- `retry_timeout_seconds` exposes retry timeout in seconds, also using `-1` for forever.
- `fail_at_unmount` is a mount-level error test/control attribute under the error directory.
- `xfs_error_meta_init` sets default metadata error policies: default, `EIO`, and `ENOSPC` retry forever, while `ENODEV` has zero retries and zero timeout.
- `xfs_error_sysfs_init_class` initializes the class directory and one kobject per errno policy, with unwind on partial failure.
- `xfs_error_get_cfg` maps runtime errno values to the default, EIO, ENOSPC, or ENODEV configuration.

## Zoned Sysfs Attributes

- Active when `CONFIG_XFS_RT` is enabled and the mount has zoned realtime support.
- `max_open_zones` reports open zones available for user data, subtracting `XFS_OPEN_GC_ZONES`.
- `nr_open_zones` reports the current open-zone count from zone info.
- `zonegc_low_space` is read/write, accepts 0 to 100, and wakes zone GC when changed.
- `xfs_zoned_ktype` groups zoned attributes.

## Mount Sysfs Lifecycle

- `xfs_mount_sysfs_init` names the superblock sysfs entry, creates the mount root, stats directory, error directory, `fail_at_unmount` file, metadata error class entries, and optional zoned directory.
- On failure it unwinds created objects in reverse order.
- `xfs_mount_sysfs_del` removes optional zoned sysfs, all error cfg kobjects, metadata error class, error root, stats dir, and mount root.

## Dependencies and Callers

- Depends on `xfs_sysfs.h`, log internals, mount state, and zoned allocation headers.
- Called by mount/log/global stats setup code elsewhere in XFS, especially `xfs_super.c`.
- Uses `xfs_stats_format` and `xfs_stats_clearall` from `xfs_stats.c`.

## Research Notes

- Kobject lifetime is completion-based through helpers in `xfs_sysfs.h`; deletion waits for release completion.
- Error policy sysfs is per mount, while stats sysfs exists both globally and per mount.
- Debug sysfs attributes directly mutate global variables and are intentionally available only in debug builds.
