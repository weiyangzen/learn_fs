# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/imager.c

## Role

Reads and writes compact filesystem metadata images: inode tables, superblock/group descriptors, and bitmaps.

## Main Flow

- `ext2fs_image_inode_write()` streams inode table blocks group by group, optionally seeking over zero blocks for sparse output.
- `ext2fs_image_inode_read()` restores inode table blocks and flushes the inode cache.
- `ext2fs_image_super_write()` writes the superblock then group descriptors, with big-endian byte swapping when needed.
- `ext2fs_image_super_read()` reads the combined superblock/descriptor image back into memory.
- Bitmap image read/write serializes inode or block bitmaps through generic bitmap range APIs and block-aligns output padding.

## Dependencies

Uses POSIX `read`, `write`, `lseek` wrappers directly, plus ext2fs I/O channels for actual filesystem block I/O and generic bitmap range helpers.

## Risks / Notes

- Unlike most ext2fs code, this file uses raw file descriptors for the image stream.
- Sparse inode image writing uses seeks to create holes; the destination fd must support seeking.
- Bitmap write returns `EXT2_ET_SHORT_READ` on short write in one path, which is semantically odd.
