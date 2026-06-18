# File Research: sources/local-fs/btrfs-linux/fs/btrfs/sysfs.h

This header declares the public sysfs interface implemented by `sysfs.c`. It forward-declares the Btrfs core types needed by callers and defines `enum btrfs_feature_set` with `FEAT_COMPAT`, `FEAT_COMPAT_RO`, `FEAT_INCOMPAT`, and `FEAT_MAX`.

The exported feature helpers are `btrfs_printable_features()` and `btrfs_feature_set_name()`. They let other code format feature-bit sets consistently with the sysfs naming table, including generated names for unknown bits.

The exported lifecycle API covers global sysfs setup/teardown, filesystem UUID kobject creation/removal, mounted filesystem sysfs setup/removal, sprout-fsid renaming, feature-group refresh, block-device uevents, and devid renaming. It also exposes allocation-space operations for adding/removing space-info and raid-profile kobjects.

The qgroup API exports add/delete functions for the global qgroups kobject and individual qgroup kobjects. These are no-ops for testing filesystems in the implementation.

`btrfs_read_policy_to_enum()` is always declared. Under `CONFIG_BTRFS_EXPERIMENTAL`, the header also declares module-parameter initialization and access for the global read-policy string.

The header is intentionally narrow: it does not expose sysfs attribute structures or kobject internals, only Btrfs-level operations used by mount, device, allocation, qgroup, and module init/exit paths.
