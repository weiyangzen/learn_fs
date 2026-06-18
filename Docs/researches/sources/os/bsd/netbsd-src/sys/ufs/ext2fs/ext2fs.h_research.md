# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs.h

This is the main ext2/ext3/ext4-compatible filesystem format and in-memory mount header.

Key definitions:
- Boot/superblock offsets and sizes: `BBSIZE`, `SBSIZE`, `BBOFF`, `SBOFF`, `BBLOCK`, `SBLOCK`.
- Block conversion and sizing macros: `fsbtodb`, `lblkno`, `blksize`, `EXT2_FSBTODB*`, `EXT2_DBTOFSB`, `ext2_blkoff`, `ext2_lblkno`, etc.
- `struct ext2fs`: on-disk superblock layout including ext2, ext3, and ext4-era fields.
- `struct m_ext2fs`: in-memory mount-time derived fields such as block size, shifts, group count, inode-per-block count, group descriptor table, read-only/modified flags, and hash signedness.
- Feature flags for compatible, read-only-compatible, and incompatible features.
- Supported feature masks: this implementation supports selected sparse super, largefile, huge file, extra inode size, dir nlink, group descriptor checksum, file type, extents, flex_bg, and 64-bit features.
- Error behavior, creator OS, clean-state flags.
- `struct ext2_gd`: ext2/ext4 block group descriptor including high 32-bit block references and checksum-related fields.
- Group descriptor checksum support macro `E2FS_HAS_GD_CSUM`.
- Sparse-super helper `cg_has_sb`.
- Endian conversion macros and byte-swap function declaration for big-endian systems.
- Inode and cylinder-group location macros.

Dependencies:
- Includes `sys/bswap.h`.
- Used broadly by all ext2fs implementation files.

Design notes:
- Superblock fields are represented with fixed-width integer types matching disk layout, but not all ext4 features listed are supported for read/write operation.
- Group descriptors are noted as not byte-swapped outside kernel context.
- Many macros assume `m_ext2fs` derived fields are initialized correctly during mount.
