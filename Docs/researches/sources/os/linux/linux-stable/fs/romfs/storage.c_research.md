# File Research: sources/os/linux/linux-stable/fs/romfs/storage.c

Backing-store abstraction for ROMFS reads and string operations over MTD and block devices.

Key responsibilities:
- Provides MTD helpers:
  - `romfs_mtd_read()` wraps `mtd_read()` and requires full-length reads.
  - `romfs_mtd_strnlen()` scans up to 16 bytes at a time for NUL.
  - `romfs_mtd_strcmp()` compares name bytes and verifies trailing NUL.
- Provides block helpers:
  - `romfs_blk_read()` reads via `sb_bread()` in ROMFS block-sized segments.
  - `romfs_blk_strnlen()` scans buffer heads for NUL.
  - `romfs_blk_strcmp()` compares across block boundaries and validates trailing NUL, including the case where NUL is the first byte of the next block.
- Public wrappers select MTD when `sb->s_mtd` exists, block when `sb->s_bdev` exists, and otherwise fail with `-EIO`.

Validation:
- `romfs_dev_read()` rejects reads outside `romfs_maxsize(sb)`.
- `romfs_dev_strnlen()` clamps max length to filesystem image end.
- `romfs_dev_strcmp()` rejects names longer than `ROMFS_MAXFN` and requires room for trailing NUL.

Purpose:
- Keeps ROMFS superblock/directory code independent of whether the image is backed by MTD or block storage.
