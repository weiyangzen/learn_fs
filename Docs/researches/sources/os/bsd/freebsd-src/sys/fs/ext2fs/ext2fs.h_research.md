# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2fs.h

## Purpose
Defines ext2/ext3/ext4 superblock layouts, in-memory filesystem state, feature flags, group descriptor layout, and core geometry macros.

## Main Elements
- `struct ext2fs` models the on-disk superblock, including ext2 base fields, ext3 journal/hash fields, ext4 64-bit counters, checksum fields, quota/project fields, MMP fields, snapshot fields, and reserved padding.
- `struct m_ext2fs` stores derived in-memory mount state: block and inode geometry, free counts, group descriptors, directory totals, cluster summaries, checksum seed, max file size, hash signing mode, and short symlink limit.
- Defines magic/revision constants, checksum algorithm code, clean/error state flags, miscellaneous hash flags, and block-group flags.
- Enumerates compat, rocompat, and incompat feature bits plus printable feature-name tables.
- Defines supported feature masks: directory hash index, sparse super, large file, group descriptor checksums, metadata checksums, directory nlink, huge file, extra inode size, file types, meta_bg, extents, 64bit, flex_bg, and checksum seed.
- `struct ext2_gd` defines group descriptor fields, including high words and bitmap checksums for 64-bit ext4-era filesystems.
- Provides feature-test macros and geometry helpers for block size, fragment size, descriptors per block, inode size, blocks per group, first inode, and Linux device major/minor limits.

## Dependencies And Integration
Included broadly across ext2fs. Mount validation, allocation, checksum, inode conversion, directory indexing, and vnode operations all depend on these definitions.

## Risk Notes
The feature support masks are mount-policy critical. Claiming support for a feature here without complete implementation elsewhere can expose read-write corruption risks.
