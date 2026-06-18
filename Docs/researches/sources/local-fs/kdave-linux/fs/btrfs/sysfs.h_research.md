# File Research: sources/local-fs/kdave-linux/fs/btrfs/sysfs.h

This header declares Btrfs sysfs types and entry points used outside `sysfs.c`.

It defines `enum btrfs_feature_set` with `FEAT_COMPAT`, `FEAT_COMPAT_RO`, `FEAT_INCOMPAT`, and `FEAT_MAX`, matching the three feature flag sets stored in the superblock.

Public declarations cover printable feature names, feature set names, sysfs fsid/device add/remove/update, mounted filesystem add/remove, block group and space-info sysfs registration, qgroup sysfs registration/deletion, feature group updates, and block-device uevents.

It also declares read-policy parsing via `btrfs_read_policy_to_enum()`. Under `CONFIG_BTRFS_EXPERIMENTAL`, it exposes read-policy module initialization and access to the module parameter string.

The header intentionally uses forward declarations for Btrfs core structures to avoid pulling large implementation headers into users of the sysfs interface.
