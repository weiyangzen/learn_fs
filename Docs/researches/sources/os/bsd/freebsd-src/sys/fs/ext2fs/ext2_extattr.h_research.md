# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_extattr.h

This header defines ext4 extended attribute namespace constants, disk structures, alignment macros, iteration macros, and exported extattr operations.

Key responsibilities:
- Define Linux xattr namespace indexes.
- Define xattr block magic and maximum name length.
- Define xattr name/value/block hash shifts.
- Declare external xattr block headers, in-inode xattr headers, and xattr entries.
- Provide alignment, size, first-entry, next-entry, and terminator macros.
- Declare inode/block list/get/set/delete/free operations.

Important definitions:
- `EXT4_XATTR_INDEX_USER`, `EXT4_XATTR_INDEX_SYSTEM`, POSIX ACL indexes, and other Linux namespace indexes.
- `EXTATTR_MAGIC`, `EXT2_EXTATTR_NAMELEN_MAX`.
- `struct ext2fs_extattr_header`, `struct ext2fs_extattr_dinode_header`, `struct ext2fs_extattr_entry`.
- `EXT2_IFIRST`, `EXT2_HDR`, `EXT2_ENTRY`, `EXT2_FIRST_ENTRY`, `EXT2_IS_LAST_ENTRY`.
- `EXT2_EXTATTR_LEN`, `EXT2_EXTATTR_SIZE`, `EXT2_EXTATTR_NEXT`.

Important interactions:
- Used by `ext2_extattr.c` for storage manipulation and by `ext2_csum.c` for external xattr block checksum coverage.
