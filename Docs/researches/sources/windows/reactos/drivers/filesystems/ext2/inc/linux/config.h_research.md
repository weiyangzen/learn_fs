# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/config.h

This small configuration header enables htree indexed-directory support.

Definitions:
- Include guard `LINUX_CONFIG_H`.
- `EXT2_HTREE_INDEX 1`.
- A commented-out alternative `#undef EXT2_HTREE_INDEX`.

Impact:
- Enables `is_dx(dir)` and related indexed-directory link-count behavior in `ext3_fs.h`.
