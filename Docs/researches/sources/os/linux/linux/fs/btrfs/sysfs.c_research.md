# File Research: sources/os/linux/linux/fs/btrfs/sysfs.c

Read completely: 2702 lines.

This file implements the Btrfs sysfs surface under `/sys/fs/btrfs`, including module-wide feature discovery, per-filesystem attributes, allocation/space-info directories, device directories and links, qgroup directories, read-policy tuning, and sysfs init/exit.

Major sysfs layout implemented here:
- `/sys/fs/btrfs/features`: supported feature-bit attributes plus static capability attributes.
- `/sys/fs/btrfs/<uuid>`: mounted filesystem attributes such as label, nodesize, sectorsize, checksum, generation, read policy, commit stats, quota override, temp fsid, and exclusive operation.
- `/sys/fs/btrfs/<uuid>/features`: currently enabled or modifiable per-filesystem feature bits.
- `/sys/fs/btrfs/<uuid>/allocation`: global reservation stats and per-space-info children.
- `/sys/fs/btrfs/<uuid>/allocation/<bg-type>`: space-info accounting, reclaim tunables, chunk-size control, and per-RAID-profile children.
- `/sys/fs/btrfs/<uuid>/discard`: async discard stats and limits.
- `/sys/fs/btrfs/<uuid>/devices` and `/devinfo/<devid>`: block-device links plus per-device state and error counters.
- `/sys/fs/btrfs/<uuid>/qgroups` and qgroup children: qgroup mode/status and per-qgroup accounting.

Feature handling:
- `struct btrfs_feature_attr` wraps a kobject attribute with feature set and bit.
- `get_features()` and `set_features()` access compat, compat_ro, or incompat flags from the superblock copy.
- `can_modify_feature()` gates mounted-filesystem feature changes through `*_SAFE_SET` and `*_SAFE_CLEAR` masks.
- `btrfs_feature_attr_show()` reports either per-filesystem state or global modifiability.
- `btrfs_feature_attr_store()` validates mounted writable filesystems, applies safe feature set/clear operations under `super_lock`, sets `BTRFS_FS_NEED_TRANS_COMMIT`, and wakes the transaction thread instead of committing directly from sysfs.
- Unknown feature bits are exposed with generated names like `compat_ro:12` through `addrm_unknown_feature_attrs()`.

Static capability attributes report POSIX ACL support, supported checksums, send stream version, rescue options, supported sectorsizes, `rmdir_subvol`, and temp-fsid support.

Discard attributes expose counters from `fs_info->discard_ctl` and writable tunables for `iops_limit`, `kbps_limit`, and `max_discard_size`. Store paths parse numeric input, update values with `WRITE_ONCE()` where appropriate, and reschedule discard work when limits change.

Allocation and space-info handling:
- Global reservation size/reserved are shown under the allocation directory.
- Per-RAID-profile kobjects report total and used bytes by iterating block groups under `groups_sem`.
- `SPACE_INFO_ATTR()` generates locked readers for core space-info accounting fields.
- `chunk_size` is writable by `CAP_SYS_ADMIN`, forbidden for system space and zoned filesystems, capped by max data chunk size and 10% of writable device bytes, and aligned to 256 MiB.
- Reclaim tunables include global and per-space-info thresholds plus dynamic/periodic reclaim switches.
- Debug builds expose `force_chunk_alloc`, which starts a transaction and requests chunk allocation from sysfs context with explicit warnings in comments.

Per-filesystem attributes:
- `label` is writable on read-write filesystems and updates the superblock label under `super_lock`, then schedules a transaction commit.
- `commit_stats` reports commit counts and durations; writing `0` as `CAP_SYS_RESOURCE` resets max commit duration.
- `quota_override` is controlled by `CAP_SYS_RESOURCE`.
- `read_policy` supports `pid`, and under experimental builds `round-robin[:value]` and `devid[:value]`. Parsing is shared with module parameter initialization through `btrfs_read_policy_to_enum()`.
- `exclusive_operation` maps the current exclusive operation enum to a readable string.

Kobject lifecycle:
- `btrfs_init_sysfs()` creates the top-level `btrfs` kset under `fs_kobj`, initializes feature attributes, and creates/merges global feature groups.
- `btrfs_exit_sysfs()` removes groups and unregisters the kset.
- `btrfs_sysfs_add_fsid()` creates the per-fsid directory plus `devices` and `devinfo` children.
- `btrfs_sysfs_add_mounted()` adds per-device entries, filesystem files, feature groups, discard directory, `bdi` link, and allocation directory; failure unwinds through `btrfs_sysfs_remove_mounted()`.
- `btrfs_sysfs_remove_mounted()` removes mounted-only files/directories but leaves fsid-level teardown to `btrfs_sysfs_remove_fsid()`.
- Device kobjects use completions so removal can wait for release callbacks.
- Space-info and RAID kobjects own their release/free paths.

Device handling:
- `btrfs_sysfs_add_device()` creates a block-device symlink and `/devinfo/<devid>` kobject.
- Device attributes expose in-filesystem-metadata, missing, replace-target, writable, fsid, scrub speed limit, and error stats.
- `btrfs_sysfs_update_sprout_fsid()` and `btrfs_sysfs_update_devid()` rename kobjects after fsid/devid changes.
- `btrfs_kobject_uevent()` sends block-device uevents and logs failures.

Qgroup handling:
- Global qgroup attributes expose enabled, mode (`qgroup` or `squota`), inconsistent, and drop-subtree threshold.
- Per-qgroup attributes expose referenced/exclusive limits and reservation buckets.
- Testing filesystems skip qgroup sysfs operations.
- Add/delete paths use qgroup kobjects under `fs_info->qgroups_kobj` and clean up on failure.

Concurrency and correctness notes:
- Superblock feature/label access uses `super_lock`.
- Space-info accounting readers use `space_info->lock`; block-group iteration uses `groups_sem`.
- Qgroup readers use `qgroup_lock`.
- Sysfs kobject creation can allocate with `GFP_KERNEL`; block-group sysfs add wraps allocation in a NOFS context to avoid reclaim deadlocks while transaction-related locks may be held.
- Feature updates avoid direct transaction commits in sysfs context.
- Store paths carefully reject readonly filesystems, missing fs devices, invalid values, unsupported operations, and insufficient capabilities.

Main risks:
- Sysfs lifecycle ordering is delicate: mounted-only teardown, fsid teardown, seeded devices, and kobject release completions must stay paired.
- Feature mutability must remain synchronized with safe set/clear masks or sysfs could expose unsafe mounted feature changes.
- New space-info subgroups, RAID profiles, qgroup fields, device states, or feature bits need matching sysfs naming and removal paths.
- Read-policy parsing differs between experimental and non-experimental builds; callers must handle unavailable policy names.
