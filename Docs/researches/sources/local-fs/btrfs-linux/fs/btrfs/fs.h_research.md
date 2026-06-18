# File Research: sources/local-fs/btrfs-linux/fs/btrfs/fs.h

## Summary
Defines central Btrfs filesystem constants, runtime state bits, mount option bits, supported feature masks, compression identifiers, and major in-memory structures such as `btrfs_fs_info`, `btrfs_free_cluster`, `btrfs_discard_ctl`, and checksum contexts.

## Main Responsibilities
- Establish global size limits and metadata sizing helpers.
- Define filesystem runtime state flags and long-lived `fs_info->flags` bits.
- Define mount option bit assignments and read-only mount option mask.
- Declare supported compat-ro and incompat feature masks.
- Define compression type identifiers and exclusive operation identifiers.
- Define core runtime structures used across Btrfs subsystems.
- Provide inline helpers for fs generation, transaction generation, metadata reservations, zoned checks, folio block counts, mount option checks, shutdown state, and test builds.

## Key Structures
- `struct btrfs_fs_info`: top-level per-mounted-filesystem state. It owns root pointers, global root tree, fs-root radix tree, block-group tree, mapping tree, reservations, transactions, worker pools, block-group reclaim lists, discard state, qgroup state, scrub state, balance state, dev-replace state, sysfs objects, cached block sizes, zoned-mode fields, commit stats, and debug-only tracking.
- `struct btrfs_free_cluster`: clustered allocation window with rb-tree of reserved free-space entries, max extent size, window start, owning block group, and locks.
- `struct btrfs_discard_ctl`: async discard work, queues, limits, current block group, discard filters, and counters.
- `struct btrfs_dev_replace`: device replacement state, progress, devices, counters, wait queues, locks, and worker task.
- `struct btrfs_delayed_root`: delayed inode/item root state and wait queue.
- `struct btrfs_commit_stats`: commit counters and durations.
- `struct btrfs_csum_ctx`: algorithm-tagged checksum context for CRC32C, xxhash64, SHA-256, and BLAKE2b.

## Key APIs and Helpers
- Metadata sizing: `btrfs_calc_insert_metadata_size()`, `btrfs_calc_metadata_size()`, `btrfs_csum_bytes_to_leaves()`, `count_max_extents()`.
- Generation access: `btrfs_get_fs_generation()`, `btrfs_set_fs_generation()`, `btrfs_get_last_trans_committed()`, `btrfs_set_last_trans_committed()`, `btrfs_set_last_root_drop_gen()`, `btrfs_get_last_root_drop_gen()`.
- Filesystem modes: `btrfs_is_zoned()`, `btrfs_is_shutdown()`, `btrfs_force_shutdown()`, `btrfs_fs_closing()`, `btrfs_need_cleaner_sleep()`.
- Mount and feature checks: `btrfs_test_opt()`, `btrfs_set_opt()`, `btrfs_clear_opt()`, `btrfs_fs_incompat()`, `btrfs_fs_compat_ro()`.
- Folio helpers: `folio_to_inode()`, `folio_to_fs_info()`, `inode_to_fs_info()`, `btrfs_blocks_per_folio()`, ordered-folio flag helpers.

## Important Behavior
`btrfs_fs_info` is the central coordination object for almost every Btrfs subsystem. Many members have explicit lock ownership in comments, including generation under `trans_lock`, root trees under root-specific locks, space info under RCU, block-group lists under `unused_bgs_lock`, and exclusive operation under `super_lock`.

Mount options include both ordinary behavior switches and full read-only options. `BTRFS_MOUNT_FULL_RO_MASK` identifies options that require a mount mode where no new transaction can be allowed.

Supported feature masks distinguish stable incompat features from experimental features. Extent tree v2, RAID stripe tree, and remap tree are only in the supported incompat mask under `CONFIG_BTRFS_EXPERIMENTAL`.

The file defines the free-space and discard structures used by `free-space-cache.c` and `discard.c`. `btrfs_free_cluster` is used to batch allocation from block groups, while `btrfs_discard_ctl` manages async discard queues and rate limiting.

Shutdown helper `btrfs_force_shutdown()` records `-EIO`, sets emergency-shutdown state, logs once, and reports the shutdown through `fserror_report_shutdown()` without directly flipping the superblock read-only flag.

## Risks
Because `btrfs_fs_info` aggregates cross-subsystem state, lock ownership and lifetime rules are spread across many users. Misusing a field without the documented lock can race mount, unmount, transaction commit, reclaim, discard, scrub, balance, or device replacement.

Feature masks define mount compatibility. Accidentally adding a feature to the wrong mask can allow unsafe mounts or reject valid filesystems.

Several helpers use `READ_ONCE()`/`WRITE_ONCE()` for fields with special transaction visibility rules. Direct access to those fields can see inconsistent state or violate ordering assumptions.
