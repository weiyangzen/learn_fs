# File Research: sources/os/linux/linux-stable/fs/btrfs/sysfs.h

## Role
Public header for Btrfs sysfs integration. It defines the feature-set enum and exposes sysfs setup, teardown, mounted filesystem, device, space-info, qgroup, feature, uevent, and read-policy helpers to the rest of Btrfs.

## Main Interfaces
- Defines `enum btrfs_feature_set` with `FEAT_COMPAT`, `FEAT_COMPAT_RO`, `FEAT_INCOMPAT`, and `FEAT_MAX`, matching the three superblock feature flag classes.
- Declares feature formatting helpers: `btrfs_printable_features` and `btrfs_feature_set_name`.
- Declares kobject/sysfs lifecycle functions: global init/exit, fsid add/remove, mounted add/remove, sprout fsid rename, feature update, devid rename, and block device uevent helper.
- Declares allocation sysfs helpers for block group profile directories and space-info directories.
- Declares qgroup sysfs add/remove helpers for the qgroups container and individual qgroups.
- Declares `btrfs_read_policy_to_enum` unconditionally and experimental module read-policy helpers only under `CONFIG_BTRFS_EXPERIMENTAL`.

## Dependencies
Uses forward declarations for Btrfs structures and includes Linux type, compiler, and kobject declarations. The header is intentionally declaration-only and contains no inline sysfs behavior except conditional prototypes.
