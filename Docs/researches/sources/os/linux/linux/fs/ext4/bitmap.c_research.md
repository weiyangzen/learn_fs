# File Research: sources/os/linux/linux/fs/ext4/bitmap.c

## Purpose
Provides ext4 bitmap utility and metadata checksum helpers.

## Main Responsibilities
- `ext4_count_free()` counts unset bits in a bitmap using `memweight()`.
- `ext4_inode_bitmap_csum_verify()` and `_set()` verify/store inode bitmap checksums in group descriptors.
- `ext4_block_bitmap_csum_verify()` and `_set()` verify/store block bitmap checksums in group descriptors.

## Integration Points
Used by block/inode allocation and bitmap validation paths. Relies on `metadata_csum`, ext4 checksum seed, descriptor size, and low/high checksum fields.

## Risks and Edge Cases
Checksum byte length differs for inode and block bitmaps. High checksum fields are present only with sufficiently large group descriptors; otherwise calculated checksums are truncated to 16 bits.
