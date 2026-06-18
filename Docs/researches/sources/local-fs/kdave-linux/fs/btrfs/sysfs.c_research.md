# File Research: sources/local-fs/kdave-linux/fs/btrfs/sysfs.c

This file implements Btrfs' sysfs interface under `/sys/fs/btrfs`, covering global feature discovery, per-filesystem attributes, device info, allocation/space-info trees, discard tunables, read policy, qgroup reporting, and module init/exit registration.

Key structures are `struct btrfs_feature_attr` for feature-bit attributes and `struct raid_kobject` for per-RAID-profile allocation directories. Attribute construction is centralized through `BTRFS_ATTR*` and `BTRFS_FEAT_ATTR*` macros, which bind sysfs names, permissions, show handlers, and store handlers.

Feature handling reads and updates compat, compat_ro, and incompat superblock flags via `get_features()` and `set_features()`. `btrfs_feature_attr_store()` permits mounted-filesystem feature changes only when the bit is listed in the safe set/clear masks, rejects read-only filesystems, updates the superblock copy under `super_lock`, and wakes the transaction thread instead of committing directly from sysfs.

The global `/sys/fs/btrfs/features` directory exposes supported feature bits plus static capability attributes such as ACL support, checksum algorithms, send stream version, rescue options, supported sector sizes, and temp-fsid support. Mounted filesystems also get a UUID-specific `features` group whose visibility depends on the filesystem’s enabled feature bits and safe modification status.

Discard sysfs attributes under `<uuid>/discard` expose async discard counters and tunables: discardable bytes/extents, bitmap/extent bytes, saved bytes, IOPS limit, KB/s limit, and max discard size. Store handlers validate numeric input, update `discard_ctl`, and reschedule discard work where appropriate.

Allocation sysfs is split into `<uuid>/allocation`, per-space-info directories such as `data`, `metadata`, `system`, `mixed`, and per-RAID-profile directories. Space-info attributes expose accounting fields, reclaim counters, size-class counts, chunk size, reclaim thresholds, and optional debug-only forced chunk allocation.

Per-filesystem attributes include label, node/sector size, clone alignment, quota override, metadata UUID, checksum name, exclusive operation state, generation, read policy, background reclaim threshold, commit stats, and temp fsid. Writable attributes perform capability checks where needed and use `READ_ONCE`/`WRITE_ONCE` or locks for shared state.

Device sysfs creates `<uuid>/devices` links to block devices and `<uuid>/devinfo/<devid>` kobjects. Per-device attributes expose error stats, fsid, in-metadata/missing/replace-target/writeable state, and scrub speed limit.

Qgroup sysfs creates `<uuid>/qgroups`, reports global qgroup enabled/inconsistent/mode/drop-subtree-threshold state, and creates one kobject per qgroup with referenced, exclusive, max, limit, and reservation counters. Testing filesystems skip qgroup sysfs creation.

Lifecycle code creates and tears down kobjects carefully: `btrfs_sysfs_add_fsid()`, `btrfs_sysfs_add_mounted()`, `btrfs_sysfs_remove_mounted()`, and `btrfs_sysfs_remove_fsid()` handle partial failure cleanup, device removal, unknown feature attributes, bdi links, discard/allocation/debug directories, and completion-based kobject release waits.

Important integration points include `btrfs_sysfs_add_block_group_type()`, `btrfs_sysfs_add_space_info_type()`, `btrfs_sysfs_update_sprout_fsid()`, `btrfs_sysfs_update_devid()`, `btrfs_sysfs_feature_update()`, `btrfs_kobject_uevent()`, `btrfs_init_sysfs()`, and `btrfs_exit_sysfs()`.
