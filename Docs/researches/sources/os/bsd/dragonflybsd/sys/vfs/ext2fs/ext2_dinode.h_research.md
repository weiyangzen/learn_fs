# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_dinode.h

This header defines the ext2/ext3/ext4 on-disk inode layout and inode-related constants used by the DragonFlyBSD ext2 implementation.

Key responsibilities:
- Declare special inode numbers, including root, journal, resize, and first normal inode.
- Define ext2/ext3/ext4 inode flags mapped to DragonFly inode flags or internal state.
- Define timestamp extra-field bit layout for epoch and nanosecond storage.
- Define direct/indirect block pointer counts and maximum inline symlink length.
- Declare `struct ext2fs_dinode`, the little-endian on-disk inode format.

Important definitions:
- `EXT2_ROOTINO`, `EXT2_FIRSTINO`, and other reserved inode numbers.
- `EXT2_APPEND`, `EXT2_IMMUTABLE`, `EXT2_NODUMP`, `EXT3_INDEX`, `EXT4_EXTENTS`, `EXT4_HUGE_FILE`, and related flags.
- `E2DI_HAS_XTIME` and `E2DI_HAS_HUGE_FILE`: Feature-gated checks for extended timestamps and large block counts.
- `EXT2_NDIR_BLOCKS`, `EXT2_IND_BLOCK`, `EXT2_DIND_BLOCK`, `EXT2_TIND_BLOCK`, `EXT2_N_BLOCKS`, `EXT2_MAXSYMLINKLEN`.
- `struct ext2fs_dinode`: Mode, ownership, size, timestamps, deletion time, link count, block count, flags, block pointers/extents, generation, EA block, high UID/GID, checksum, extra timestamp, birth time, and project ID fields.

Important interactions:
- Used by inode conversion in `ext2_inode_cnv.c`, inode checksum code in `ext2_csum.c`, allocation and truncation code, and symlink handling elsewhere in ext2fs.

Notable behavior:
- The block array is reused as extent tree storage when `EXT4_EXTENTS` is set.
- Only selected ext4-era fields are represented; support depends on feature checks in mount and conversion code.
