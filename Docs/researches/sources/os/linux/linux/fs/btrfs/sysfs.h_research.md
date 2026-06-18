# File Research: sources/os/linux/linux/fs/btrfs/sysfs.h

Read completely: 57 lines.

This header declares the public Btrfs sysfs interface used by the rest of the filesystem.

It defines `enum btrfs_feature_set` with the three superblock feature namespaces:
- `FEAT_COMPAT`
- `FEAT_COMPAT_RO`
- `FEAT_INCOMPAT`

Exports include:
- Feature formatting helpers: `btrfs_printable_features()` and `btrfs_feature_set_name()`.
- Top-level sysfs lifecycle: `btrfs_init_sysfs()` and `btrfs_exit_sysfs()`.
- Fsid and mounted-filesystem lifecycle: `btrfs_sysfs_add_fsid()`, `btrfs_sysfs_remove_fsid()`, `btrfs_sysfs_add_mounted()`, and `btrfs_sysfs_remove_mounted()`.
- Device lifecycle and rename/update helpers: `btrfs_sysfs_add_device()`, `btrfs_sysfs_remove_device()`, `btrfs_sysfs_update_devid()`, and `btrfs_sysfs_update_sprout_fsid()`.
- Allocation sysfs helpers for block groups and space info.
- Qgroup sysfs add/delete helpers.
- Read policy parser `btrfs_read_policy_to_enum()`.
- Experimental read-policy module-parameter helpers when `CONFIG_BTRFS_EXPERIMENTAL` is enabled.

The header intentionally forward-declares Btrfs structures so sysfs users do not need to include the implementation-heavy headers directly.
