# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_types.h

Primary on-disk ext4 and JBD type-definition header. It defines ext block number typedefs, superblock, group descriptor, inode, directory, htree, extent, and journal structures, plus most ext4/JBD feature bits and constants.

Key behavior:
- Defines `ext4_lblk_t` and `ext4_fsblk_t`, checksum and UUID constants, and maps allocation macros to Plan 9 libc allocation routines.
- Defines packed `ext4_sblock` with standard ext4 superblock fields through checksum.
- Defines ext4 magic, superblock size/offset, OS IDs, filesystem flags, filesystem states, error behavior, compatible/read-only/incompatible feature masks, supported feature masks for ext2/ext3/ext4, and ignored incompatible masks.
- Defines packed `ext4_bgroup`, descriptor sizes, block size limits, inode block constants, and packed `ext4_inode`.
- Defines inode modes and inode flags.
- Defines directory entry file types, directory entry and htree root/node/tail structures, checksum tail structures, special inode numbers, link max, and htree hash constants.
- Defines packed extent tail, extent, extent index, and extent header structures and extent magic.
- Defines JBD magic, block types, block header, checksum types, commit header, block tags, tag flags, descriptor/revoke tails, revoke header, journal superblock, and JBD feature masks.

Notable dependencies:
- Includes `ext4_blockdev.h` and `tree.h`, making this central header mutually important to the rest of ext4srv.
- Consumed by nearly every implementation and public header.

Research notes:
- Structures are packed with Plan 9 `#pragma pack on/off` to match disk layout.
- The supported ext4 feature mask includes features later disabled by `ext4_mkfs`, because mount/read support and mkfs defaults are handled separately.
- The ignored feature comment says journaling is not supported, which is stale relative to this batch's JBD implementation.
