# File Research: sources/local-fs/btrfs-linux/fs/btrfs/sysfs.c

This file implements Btrfs' `/sys/fs/btrfs` interface. It creates global feature advertisement, per-filesystem UUID directories, mounted filesystem attributes, device and devid directories, allocation and raid-profile statistics, discard statistics and tunables, qgroup directories, and runtime feature visibility updates.

The file defines local wrappers around `struct kobj_attribute` and `struct kobject` ownership: `struct btrfs_feature_attr` couples a sysfs file to a feature-set bit, and `struct raid_kobject` stores a raid profile flag plus a kobject. The `BTRFS_ATTR*` and `BTRFS_FEAT_ATTR*` macros build the concrete read-only, write-only, read-write, and feature-bit attributes.

Feature handling is centered on `get_features()`, `set_features()`, `can_modify_feature()`, `btrfs_feature_attr_show()`, `btrfs_feature_attr_store()`, and `btrfs_feature_visible()`. Mounted filesystems expose only enabled or safely mutable features, while the global `/sys/fs/btrfs/features` directory advertises supported feature bits. Writable feature changes are limited by the safe set/clear masks, reject read-only superblocks, update the in-memory superblock under `super_lock`, and wake the transaction thread by setting `BTRFS_FS_NEED_TRANS_COMMIT`.

The static feature group reports kernel-version capabilities independent of a mounted filesystem: ACL support, `rmdir_subvol`, supported checksums, send-stream version, rescue options, supported sector sizes, and `temp_fsid`. Unknown on-disk feature bits are represented by generated names like `compat_ro:NN` via `init_feature_attrs()` and `addrm_unknown_feature_attrs()` so mounted filesystems remain inspectable even with unsupported bits present.

Discard sysfs support uses a `discard` subdirectory and exposes `discardable_bytes`, `discardable_extents`, bitmap/extent accounting, saved bytes, and tunables for IOPS, KB/s, and maximum discard size. Store paths parse numeric input, update `fs_info->discard_ctl` with `WRITE_ONCE()` where needed, recalculate delay for IOPS, and reschedule async discard work.

Allocation sysfs support has an `allocation` directory with global reserve counters, per-space-info directories, and per-raid-profile directories. Space-info files expose bytes counters, flags, chunk size, size-class counts, reclaim stats, dynamic/periodic reclaim knobs, and optional debug-only forced chunk allocation. Chunk-size writes require `CAP_SYS_ADMIN`, reject zoned and system spaces, clamp to Btrfs limits and 10% of writable bytes, and align to 256 MiB.

The mounted filesystem root attributes include label, nodesize, sectorsize, clone alignment, quota override, metadata UUID, checksum type, exclusive operation, generation, read policy, block-group reclaim threshold, commit stats, and temporary-fsid state. Label and feature writes intentionally defer persistence through normal transaction commit rather than committing directly from sysfs context.

Read-policy support always includes `pid` and conditionally includes experimental `round-robin[:value]` and `devid[:value]`. `btrfs_read_policy_to_enum()` parses optional values; `btrfs_read_policy_store()` validates alignment and device IDs, toggles round-robin stats collection, and updates `fs_devices` policy fields with `WRITE_ONCE()`.

Device sysfs support creates `devices` links to block-device kobjects and `devinfo/<devid>` directories with state and statistics files: metadata membership, missing, replace-target, scrub speed limit, writeable, fsid, and error stats. Add/remove paths use NOFS context to avoid reclaim deadlocks and wait on completion when kobjects are torn down.

Filesystem and mount lifecycle functions are the public surface used elsewhere: `btrfs_init_sysfs()`, `btrfs_exit_sysfs()`, `btrfs_sysfs_add_fsid()`, `btrfs_sysfs_remove_fsid()`, `btrfs_sysfs_add_mounted()`, and `btrfs_sysfs_remove_mounted()`. They carefully build and dismantle the UUID directory, devices/devinfo subtrees, feature groups, debug groups, discard directory, BDI link, allocation directory, and per-device entries.

Qgroup sysfs support adds global `qgroups` attributes for enabled state, mode, inconsistency, and drop-subtree threshold, plus per-qgroup directories named `<level>_<subvolid>` with referenced/exclusive counts, limits, and reservation counters. Testing filesystems bypass qgroup sysfs creation/deletion through `btrfs_is_testing()`.

Key dependencies include `ctree.h`, `discard.h`, `disk-io.h`, `transaction.h`, `volumes.h`, `space-info.h`, `block-group.h`, `qgroup.h`, `fs.h`, and `accessors.h`. The file is mostly glue between core Btrfs state and Linux kobject/sysfs APIs, with important locking on superblock, qgroup, block reserve, space-info, and block-group list state.
