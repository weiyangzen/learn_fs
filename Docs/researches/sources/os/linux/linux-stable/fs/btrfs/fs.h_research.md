# File Research: sources/os/linux/linux-stable/fs/btrfs/fs.h

## Purpose

Defines central Btrfs filesystem-wide constants, feature/mount/state flags, major runtime structures, checksum interfaces, exclusive operation APIs, and common inline helpers. It is a foundational header used by the free-space cache/tree code and most Btrfs modules.

## Constants And Feature Masks

The header defines block-size limits, max extent size, max trim length, superblock location/size, metadata reservation formulas, checksum formatting, and common key formatting. It enumerates supported compat-ro and incompat feature masks, including `FREE_SPACE_TREE`, `FREE_SPACE_TREE_VALID`, `BLOCK_GROUP_TREE`, stable incompat features, and experimental features such as extent tree v2/remap/stripe tree when configured.

Mount option bits include space-cache and free-space-tree options (`SPACE_CACHE`, `CLEAR_CACHE`, `FREE_SPACE_TREE`, `NOSPACECACHE`) as well as discard, compression, degraded, ref-verify, checksum-ignore, and full-read-only options. `BTRFS_MOUNT_FULL_RO_MASK` identifies options that require no new transactions.

## Runtime State Flags

Two flag enums distinguish filesystem state and operational flags. Relevant free-space-related bits include `BTRFS_FS_CREATING_FREE_SPACE_TREE`, `BTRFS_FS_CLEANUP_SPACE_CACHE_V1`, `BTRFS_FS_FREE_SPACE_TREE_UNTRUSTED`, `BTRFS_FS_DISCARD_RUNNING`, `BTRFS_FS_FEATURE_CHANGED`, and zoned tracking flags. Shutdown and read-only helpers use `fs_state`.

## Major Structures

- `struct btrfs_dev_replace`: tracks device replacement state, cursors, errors, scrub progress, synchronization, and worker task.
- `struct btrfs_free_cluster`: holds allocation-cluster rbtrees, max size/window start, fragmentation state, owning block group, and list hook. Free-space cache code fills and drains these clusters.
- `struct btrfs_discard_ctl`: manages async discard workqueues, discard lists, rate limits, max discard size, accounting, and saved discard bytes. Free-space trimming updates this.
- `struct btrfs_fs_info`: the central per-filesystem object, containing root pointers, global root registry, block-group tree, mapping tree, block reservations, transaction state, mount options, locks, worker pools, dirty/caching block-group lists, allocation clusters, discard control, qgroup state, zoned state, block size/checksum settings, exclusive operation state, and debugging fields.

## Inline Helpers

The header provides helpers for deriving `btrfs_fs_info` from folios/inodes, computing allocation GFP masks without filesystem recursion, reading/writing generation fields with `READ_ONCE`/`WRITE_ONCE`, checksum leaf calculations, metadata reservation sizing, zoned mode detection, max-extent counting, blocks per folio, mount option manipulation, feature flag macros, closing/cleaner/shutdown checks, emergency shutdown, and ordered-folio flag aliases.

## API Declarations

It declares checksum helpers from `fs.c`, exclusive operation helpers, ioctl path validation, supported block-size validation, feature flag mutation helpers, and test-only inode destruction support. `EXPORT_FOR_TESTS` resolves to either external or static visibility depending on sanity-test configuration.

## Integration Notes

For this group, `fs.h` supplies `struct btrfs_fs_info`, `struct btrfs_free_cluster`, `struct btrfs_discard_ctl`, mount option bits, feature flag macros, block-size fields, zoned detection, checksum context declarations, and filesystem state flags used by `free-space-cache.c` and `free-space-tree.c`. The locking fields in `btrfs_fs_info` define much of the surrounding concurrency contract.
