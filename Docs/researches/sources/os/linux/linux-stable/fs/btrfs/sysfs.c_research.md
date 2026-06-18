# File Research: sources/os/linux/linux-stable/fs/btrfs/sysfs.c

## Role
Implements Btrfs' sysfs surface under `/sys/fs/btrfs`: global feature reporting, per-filesystem feature state, mounted filesystem attributes, allocation and RAID profile stats, discard tunables, per-device information, qgroup state, kobject lifecycle, and sysfs updates after runtime state changes.

## Main Interfaces and Data
- Defines local sysfs wrapper types: `struct btrfs_feature_attr` for feature-bit attributes and `struct raid_kobject` for allocation profile directories.
- Uses attribute macros (`BTRFS_ATTR`, `BTRFS_ATTR_RW`, `BTRFS_FEAT_ATTR_*`) to declare many `struct kobj_attribute` instances and feature attributes.
- Exports the public helpers declared in `sysfs.h`: `btrfs_init_sysfs`, `btrfs_exit_sysfs`, `btrfs_sysfs_add_fsid`, `btrfs_sysfs_remove_fsid`, `btrfs_sysfs_add_mounted`, `btrfs_sysfs_remove_mounted`, device helpers, qgroup helpers, feature helpers, and read-policy parsing.
- Maintains the module-level `btrfs_kset` for `/sys/fs/btrfs` and uses `btrfs_ktype` to tie an fsid kobject back to `struct btrfs_fs_devices`.

## Behavior
- Feature handling reads and mutates superblock compat, compat-ro, and incompat flags through `get_features` and `set_features`. Mounted-filesystem writes are allowed only for feature bits present in the safe set/clear masks, reject read-only mounts, update the in-memory superblock under `super_lock`, set `BTRFS_FS_NEED_TRANS_COMMIT`, and wake the transaction thread.
- Global `/sys/fs/btrfs/features` combines supported feature-bit attributes with static capabilities such as ACL support, supported checksums, send stream version, rescue options, supported sectorsizes, and `temp_fsid` support. Per-filesystem `features` visibility hides unsupported unset bits but exposes enabled or mutable bits.
- Unknown feature bits are represented through generated names like `<feature_set>:<bit>` and merged into per-filesystem feature groups by `addrm_unknown_feature_attrs`.
- Mounted filesystem attributes include `label`, `nodesize`, `sectorsize`, `clone_alignment`, `quota_override`, `metadata_uuid`, `checksum`, `exclusive_operation`, `generation`, `read_policy`, `bg_reclaim_threshold`, `commit_stats`, and `temp_fsid`.
- Read policy supports the stable `pid` mode and, under `CONFIG_BTRFS_EXPERIMENTAL`, `round-robin[:value]` and `devid[:value]`, with value parsing, sectorsize alignment for round-robin minimum contiguous reads, device-id validation for devid mode, and logging when policy changes.
- Discard sysfs exposes async discard counters and tunables: discardable bytes/extents, bitmap/extent bytes, bytes saved, IOPS limit, KB/s limit, and max discard size. Stores update `discard_ctl` with `WRITE_ONCE` and reschedule discard work where needed.
- Allocation sysfs exposes global block reserve size/reserved bytes, space-info counters, chunk size, size-class counts, reclaim counters, dynamic/periodic reclaim flags, and per-RAID profile total/used byte aggregation from block group lists.
- Chunk-size writes require `CAP_SYS_ADMIN`, reject zoned and system-space changes, parse memparse values, clamp to max data chunk size and 10 percent of total writable bytes, enforce 256 MiB alignment/minimum, and update the space-info chunk size.
- Device sysfs creates `/devices` links to block-device kobjects and `/devinfo/<devid>` directories with `error_stats`, `fsid`, `in_fs_metadata`, `missing`, `replace_target`, `scrub_speed_max`, and `writeable`.
- Qgroup sysfs creates `/qgroups` global status (`enabled`, `inconsistent`, `drop_subtree_threshold`, `mode`) and one directory per qgroup with referenced/exclusive/limit/reservation counters.

## Lifecycle and Error Handling
- `btrfs_init_sysfs` creates the global `btrfs` kset, initializes known and unknown feature attributes, creates feature groups, merges static feature attributes, and conditionally creates debug groups. `btrfs_exit_sysfs` reverses those operations.
- `btrfs_sysfs_add_fsid` creates the fsid kobject plus `devices` and `devinfo` subdirectories; failure tears down previously created objects.
- `btrfs_sysfs_add_mounted` adds device sysfs entries, per-fs attributes, features, optional debug directory, discard directory, unknown feature attrs, `bdi` link, and allocation directory. A single failure path calls `btrfs_sysfs_remove_mounted`.
- Kobject release callbacks zero embedded kobject fields and complete unregister completions for fsid and devid objects; dynamically allocated raid, space-info, and qgroups kobjects are freed by release callbacks.
- Several allocation paths enter a NOFS context before kobject creation to avoid reclaim recursion while Btrfs transaction or allocation locks may be held.

## Dependencies
This file is tightly coupled to Btrfs superblock feature definitions, fs/device structs, block group and space-info accounting, discard scheduling, qgroup state, transaction commit signaling, and Linux kobject/sysfs APIs.
