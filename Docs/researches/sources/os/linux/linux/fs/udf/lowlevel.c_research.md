# File Research: sources/os/linux/linux/fs/udf/lowlevel.c

## Purpose
Provides low-level optical/block-device helpers for locating UDF media boundaries and multisession starts.

## Main Functions
- `udf_get_last_session()`: queries CD-ROM multisession information and returns the XA session LBA when available.
- `udf_get_last_block()`: queries last written CD-ROM block; falls back to block device size when CD-ROM query fails or is unavailable.

## Important Design Points
- Uses the CD-ROM layer when the underlying disk has a `cdrom_device_info`.
- Falls back gracefully for non-CD media by using `sb_bdev_nr_blocks()`.
- Returns zero on unsupported or unusable results.

## Cross-File Relationships
- Used by UDF mount/superblock scanning code outside this group to determine where to search for descriptors.
- Depends on `udf_sb.h` and Linux block/CD-ROM APIs.

## Risks / Review Notes
- Device-size fallback returns zero if block count does not fit in `udf_pblk_t`.
- `udf_get_last_block()` returns `lblock - 1`, so callers must treat zero carefully as both possible first block and failure-like value.
