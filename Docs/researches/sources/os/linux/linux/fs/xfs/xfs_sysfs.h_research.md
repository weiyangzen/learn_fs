# File Research: sources/os/linux/linux/fs/xfs/xfs_sysfs.h

## Purpose

`xfs_sysfs.h` declares XFS sysfs kobject types and provides small helpers for kobject initialization, deletion, release completion, and mount sysfs lifecycle.

## Main Interfaces

- External kobject types: `xfs_dbg_ktype`, `xfs_log_ktype`, and `xfs_stats_ktype`.
- `to_kobj(struct kobject *kobject)`: maps a generic kobject to `struct xfs_kobj`.
- `xfs_sysfs_release`: completes the embedded completion when a kobject is released.
- `xfs_sysfs_init`: initializes completion and calls `kobject_init_and_add` with an optional parent `xfs_kobj`.
- `xfs_sysfs_del`: deletes, puts, and waits for release completion.
- `xfs_mount_sysfs_init` / `xfs_mount_sysfs_del`: per-mount sysfs lifecycle declarations.

## Implementation Notes

- `xfs_sysfs_init` calls `kobject_put` on initialization failure, matching kobject lifetime rules.
- `xfs_sysfs_del` waits synchronously for release completion, which protects embedded kobjects inside longer-lived XFS structs.
- Parent linkage is based on `struct xfs_kobj`, but the helper accepts a null parent for top-level sysfs objects under the kset configured by callers.

## Dependencies and Callers

- Used by `xfs_sysfs.c` for all kobject types.
- Used by `xfs_super.c` to create global stats/debug sysfs objects and by mount code to manage per-mount sysfs state.

## Research Notes

- This header encodes the expected XFS sysfs lifetime pattern: embedded kobject plus completion, with synchronous teardown.
