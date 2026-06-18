# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2fs.h

Defines the ext2/ext3/ext4 on-disk superblock structure, in-memory superblock structure, block group descriptor structure, feature bit definitions, feature name tables, supported-feature masks, and core ext2 sizing/access macros.

`struct ext2fs` models the 1024-byte ext-family superblock, including classic ext2 fields, dynamic revision fields, ext3 journal metadata, directory hash seed/version, 64-bit block counts, extra inode size, RAID/MMP/flex_bg metadata, lifetime write counters, snapshot/quota/project fields, error reporting fields, encryption metadata, checksum seed, and superblock checksum.

`struct m_ext2fs` is DragonFlyBSD’s in-memory superblock state. It stores the copied on-disk superblock, mount path, read-only/modified flags, expanded 64-bit block counts, block/inode geometry, group descriptor array, cluster summary data, directory count, max file size, hash signedness, and checksum seed.

Feature support is centralized here. The header names compat, ro-compat, and incompat feature bits, provides human-readable feature tables, and defines supported masks: compat support is essentially directory hash indexes; ro-compat support includes sparse superblocks, large files, GDT checksums, metadata checksums, dir_nlink, huge files, and extra inode size; incompat support includes file types, meta_bg, extents, 64-bit, flex_bg, and checksum seed.

The header defines `EXT2_HAS_COMPAT_FEATURE`, `EXT2_HAS_RO_COMPAT_FEATURE`, and `EXT2_HAS_INCOMPAT_FEATURE`, all reading little-endian feature fields from `m_ext2fs`. These macros are used heavily by mount validation, vnode ops, directory checksum handling, and pathconf.

`struct ext2_gd` supports both classic and ext4 64-bit block group descriptors, including low/high block/inode bitmap and inode table pointers, free counts, directory counts, flags, unused inode counts, and bitmap/group descriptor checksums. `E2FS_REV0_GD_SIZE` is half the ext4 descriptor size, while `E2FS_64BIT_GD_SIZE` is the full descriptor.

The bottom section provides compatibility shims for DragonFlyBSD: SDT probe macros are no-ops, `printf` maps to `kprintf`, `malloc` maps to `kmalloc`, `free` maps to `ext2_free`, lock assertions map to vnode lock checks, and `DOINGASYNC` checks `MNT_ASYNC`.

Important dependencies: consumed by `ext2_vfsops.c`, `ext2_vnops.c`, allocation, checksum, directory, and extent code. It assumes callers pass `struct m_ext2fs *` into feature macros, despite the `EXT2_SB` naming.

Notable risks or research hooks: comments under “Features supported” understate current masks compared with later ext4 feature additions. The `free(addr, type)` macro rewrites all frees through `ext2_free`, so memory accounting/debug behavior depends on that helper.
