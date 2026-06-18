# File Research: sources/local-fs/btrfs-linux/fs/btrfs/disk-io.h

## Summary
Declares the public interface for Btrfs disk I/O, root management, superblock handling, mount lifecycle, metadata validation, log tree setup, and transaction cleanup.

## Main Contents
- Superblock mirror constants: `BTRFS_SUPER_MIRROR_MAX`, `BTRFS_SUPER_MIRROR_SHIFT`.
- Fixed block-device block size: `BTRFS_BDEV_BLOCKSIZE`.
- `btrfs_sb_offset()` helper for primary and backup superblock locations.
- Function declarations for mount/open/close, root lookup/loading, metadata reads, super writes, and cleanup.

## Key Interfaces
Important declarations include `open_ctree()`, `close_ctree()`, `btrfs_start_pre_rw_mount()`, `btrfs_validate_super()`, `btrfs_check_features()`, `write_all_supers()`, `btrfs_commit_super()`, `read_tree_block()`, `btrfs_validate_extent_buffer()`, `btrfs_read_extent_buffer()`, `btree_csum_one_bio()`, root lookup helpers, global root helpers, and transaction cleanup helpers.

## Important Details
`btrfs_sb_offset()` encodes Btrfs fixed superblock mirror placement: the primary uses `BTRFS_SUPER_INFO_OFFSET`, while mirrors shift from 16 KiB by `BTRFS_SUPER_MIRROR_SHIFT`.

`btrfs_grab_root()` is an inline reference helper that increments a root refcount only if nonzero, preventing resurrection after final put.

## Risks
Most declarations here expose lifetime-sensitive root and metadata-buffer APIs. Callers must pair returned roots with `btrfs_put_root()` and must pass correct parent-check data when reading tree blocks.
