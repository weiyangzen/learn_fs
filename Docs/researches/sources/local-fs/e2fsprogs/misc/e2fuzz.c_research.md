# File Research: sources/local-fs/e2fsprogs/misc/e2fuzz.c

## Purpose
Implements `e2fuzz`, a test utility that corrupts bytes in ext filesystems or filesystem images to exercise fsck and kernel robustness.

## Main Behaviors
- Defaults to corrupting metadata only.
- Options:
  - `-b N` or `-b P%`: corrupt exact byte count or percentage of corruptible bytes.
  - `-d`: include data blocks.
  - `-n`: dry run.
  - `-v`: verbose corruption log.
- Forces dry-run mode if the filesystem is mounted read-write.
- Opens filesystem via ext2fs and refuses filesystems with error state.
- If filesystem is unclean but not in error state, switches to dry run.
- Builds a bitmap of corruptible blocks:
  - All used blocks in data mode.
  - Metadata blocks, inode tables, bitmaps, xattrs, directories, metadata-bearing file blocks, and indirect/extent metadata in metadata-only mode.
- Randomly chooses byte offsets within marked blocks and writes random bytes, skipping the first 4096 bytes to avoid the primary superblock area.

## Important Functions
- `getseed`: reads random seed from `/dev/urandom`.
- `find_block_helper`: marks blocks to corrupt based on inode type and metadata/data mode.
- `find_metadata_blocks`: marks filesystem structural metadata and scans all allocated inodes.
- `rand_num`: generates a random integer in a range using `random()`.
- `process_fs`: full safety check, bitmap creation, corruption loop, and cleanup.
- `print_help` / `main`: CLI handling.

## Dependencies
- ext2fs open, mount-state, bitmap, inode scan, and block iteration APIs.
- POSIX file I/O, with fallback `my_pwrite` if `pwrite`/`pwrite64` are unavailable.

## Notes and Edge Cases
- Metadata-only mode still includes directory data blocks because corrupting directories tests metadata repair paths.
- When using data mode, `corrupt_map` aliases `fs->block_map`; cleanup avoids freeing it twice.
- The program writes bytes directly to the backing file/device, bypassing ext2fs write helpers.
