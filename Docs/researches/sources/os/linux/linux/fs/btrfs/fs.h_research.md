# File Research: sources/os/linux/linux/fs/btrfs/fs.h

## Purpose
Central Btrfs filesystem header. It defines filesystem-wide constants, mount option bits, feature masks, core runtime state structures, checksum context, helper macros, and inline accessors used across the Btrfs implementation.

## Constants and Limits
- `BTRFS_MIN_BLOCKSIZE`: 4 KiB normally, 2 KiB in debug builds for subpage testing.
- `BTRFS_MAX_BLOCKSIZE`: 64 KiB.
- `BTRFS_MAX_EXTENT_SIZE`: 128 MiB.
- `BTRFS_MAX_TRIM_LENGTH`: 2 GiB per trim iteration.
- Superblock offset/size constants and static assertion for `struct btrfs_super_block`.
- Formatting helpers for checksums and keys.
- Metadata reservation estimate helpers:
  - `btrfs_calc_insert_metadata_size()`
  - `btrfs_calc_metadata_size()`
  - `btrfs_csum_bytes_to_leaves()`

## Filesystem State Flags
Defines two major bit groups:
- `BTRFS_FS_STATE_*`: runtime state such as remounting, read-only, transaction aborted, log replay aborted, device replace, emergency shutdown, and test dummy fs.
- `BTRFS_FS_*`: operational flags such as log recovery, quota enabled, creating free-space tree, cleanup space-cache-v1, free-space-tree untrusted, balance/relocation running, discard running, feature changed, and transaction commit requests.

Free-space-related flags:
- `BTRFS_FS_CREATING_FREE_SPACE_TREE`
- `BTRFS_FS_CLEANUP_SPACE_CACHE_V1`
- `BTRFS_FS_FREE_SPACE_TREE_UNTRUSTED`
- `BTRFS_FS_DISCARD_RUNNING`

## Mount Options and Feature Masks
- Mount option bits include `SPACE_CACHE`, `CLEAR_CACHE`, `FREE_SPACE_TREE`, `DISCARD_SYNC`, `DISCARD_ASYNC`, `NODISCARD`, and many unrelated Btrfs options.
- Compat-ro supported feature mask includes `FREE_SPACE_TREE` and `FREE_SPACE_TREE_VALID`.
- Incompat supported masks include stable features and optional experimental features such as `EXTENT_TREE_V2`, `RAID_STRIPE_TREE`, and `REMAP_TREE`.

## Free-Space-Relevant Structures
- `struct btrfs_free_cluster`
  - Holds a cluster rb-tree, max extent size, window start, owning block group, and block-group list linkage.
  - Used by free-space-cache allocation paths.
- `struct btrfs_discard_ctl`
  - Workqueue, delayed work, discard lists, current block group, rate limits, max discard size, counters, and saved-discard-byte accounting.
  - Used by free-space-cache trimming and async discard.
- `struct btrfs_fs_info`
  - The central per-mounted-filesystem object.
  - Contains all root pointers, block-group cache tree, mapping tree, reservations, transactions, mount options, workqueues, locks, discard control, zoned state, free clusters, block sizes, feature state, commit stats, and many subsystem controls.
  - Fields directly relevant to this group include:
    - `block_group_cache_tree`
    - `mount_opt`
    - `super_lock`
    - `super_copy`
    - `discard_ctl`
    - `data_alloc_cluster`
    - `meta_alloc_cluster`
    - `unused_bgs`, `fully_remapped_bgs`
    - `zone_size`, `max_extent_size`
    - `flags` bits for free-space tree/cache state.

## Checksum Context
- `struct btrfs_csum_ctx` holds streaming checksum state for CRC32C, XXHASH64, SHA256, or BLAKE2b.
- Prototypes match implementations in `fs.c`.

## Inline Helpers and Macros
- Inode/fs-info conversions:
  - `folio_to_inode()`
  - `folio_to_fs_info()`
  - `inode_to_fs_info()`
- Block/folio helpers:
  - `btrfs_alloc_write_mask()`
  - `btrfs_min_folio_size()`
  - `btrfs_blocks_per_folio()`
  - `btrfs_is_zoned()`
  - `count_max_extents()`
- Generation accessors:
  - `btrfs_get_fs_generation()`
  - `btrfs_set_fs_generation()`
  - `btrfs_get_last_trans_committed()`
  - `btrfs_set_last_trans_committed()`
- Feature flag macros:
  - `btrfs_set_fs_incompat()`, `btrfs_clear_fs_incompat()`, `btrfs_fs_incompat()`
  - `btrfs_set_fs_compat_ro()`, `btrfs_clear_fs_compat_ro()`, `btrfs_fs_compat_ro()`
- Mount option macros:
  - `btrfs_set_opt()`, `btrfs_clear_opt()`, `btrfs_test_opt()`
- Shutdown and cleaner helpers:
  - `btrfs_fs_closing()`
  - `btrfs_need_cleaner_sleep()`
  - `btrfs_is_shutdown()`
  - `btrfs_force_shutdown()`

## Design Notes
This file is not a single subsystem implementation; it is the shared state contract for the Btrfs filesystem. The free-space cache and free-space tree code rely on it for mount options, feature flags, discard control, block sizes, zoned mode checks, cluster structures, and global filesystem locks.
