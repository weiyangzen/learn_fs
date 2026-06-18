# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_dinode.h

This header defines ext2/ext3/ext4 on-disk inode constants and the FreeBSD representation of the disk inode layout.

Key responsibilities:
- Define reserved inode numbers, including root, journal, resize, exclude, and first normal inode.
- Define ext2/ext3/ext4 inode flags used for FreeBSD flags and internal state.
- Define extended timestamp epoch/nanosecond bit fields.
- Define direct/indirect block pointer counts and inline symlink capacity.
- Declare `struct ext2fs_dinode`.

Important definitions:
- `EXT2_BADBLKINO`, `EXT2_ROOTINO`, `EXT2_FIRSTINO`, and related reserved inode constants.
- `EXT2_APPEND`, `EXT2_IMMUTABLE`, `EXT2_NODUMP`, `EXT3_INDEX`, `EXT4_EXTENTS`, `EXT4_HUGE_FILE`, `EXT4_INLINE_DATA`, and related flags.
- `E2DI_HAS_XTIME`, `E2DI_HAS_HUGE_FILE`.
- `EXT2_NDIR_BLOCKS`, `EXT2_IND_BLOCK`, `EXT2_DIND_BLOCK`, `EXT2_TIND_BLOCK`, `EXT2_N_BLOCKS`, `EXT2_MAXSYMLINKLEN`.
- `struct ext2fs_dinode`: mode, ownership, size, timestamps, link count, block count, flags, block/extent array, generation, xattr block, high UID/GID, checksum, extra timestamp, birth time, and project ID fields.

Important interactions:
- Used by inode conversion, checksum, allocation, extents, extattrs, and truncation code.
- The `e2di_blocks` array is reused as extent root storage when `EXT4_EXTENTS` is set.
