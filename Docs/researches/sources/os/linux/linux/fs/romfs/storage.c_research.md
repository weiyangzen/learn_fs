# File Research: sources/os/linux/linux/fs/romfs/storage.c

## Purpose
Implements low-level ROMFS image access for MTD and block-device backing stores. It provides bounded read, string length, and string compare helpers used by ROMFS metadata parsing.

## Main Responsibilities
- Read arbitrary byte ranges from a ROMFS image.
- Compute bounded NUL-terminated string lengths inside the image.
- Compare a supplied filename string against an image string and verify its terminating NUL.
- Dispatch to MTD or block-device implementations depending on superblock backing.

## MTD Path
Compiled under `CONFIG_ROMFS_ON_MTD`:
- `romfs_mtd_read()`
  - Calls `mtd_read()` and requires the exact requested length.
- `romfs_mtd_strnlen()`
  - Reads up to 16 bytes at a time and searches for NUL.
- `romfs_mtd_strcmp()`
  - Reads up to 17 bytes at a time to compare data plus trailing NUL.

## Block Path
Compiled under `CONFIG_ROMFS_ON_BLOCK`:
- `romfs_blk_read()`
  - Reads block-sized segments through `sb_bread()`, copies from buffer heads, and releases them.
- `romfs_blk_strnlen()`
  - Scans block segments for NUL using buffer heads.
- `romfs_blk_strcmp()`
  - Compares block segments and verifies trailing NUL either in the same block or first byte of the next block.

## Public Internal API
- `romfs_dev_read(sb, pos, buf, buflen)`
  - Bounds-checks against `romfs_maxsize(sb)`.
  - Dispatches to MTD when `sb->s_mtd` is present or block when `sb->s_bdev` is present.
- `romfs_dev_strnlen(sb, pos, maxlen)`
  - Bounds-checks and clamps max length to remaining image size.
- `romfs_dev_strcmp(sb, pos, str, size)`
  - Rejects names larger than `ROMFS_MAXFN`.
  - Requires room for trailing NUL.
  - Dispatches to matching backing store.

## Error Handling
- Returns `-EIO` for out-of-range image reads, missing backing store, failed block reads, short MTD reads, or insufficient room for required data.
- Returns `-ENAMETOOLONG` for filename compare sizes greater than `ROMFS_MAXFN`.
- String compare returns `1` for match, `0` for mismatch, and negative errno on read/bounds error.

## Research Notes
This file is the storage abstraction for ROMFS metadata and file reads. Its main invariants are strict image bounds, exact-length MTD reads, buffer-head release on every block path, and correct NUL verification across block boundaries.
