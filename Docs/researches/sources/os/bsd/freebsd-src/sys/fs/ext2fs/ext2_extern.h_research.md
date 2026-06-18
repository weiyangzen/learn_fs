# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_extern.h

This header declares the cross-file ext2fs API used by allocation, mapping, inode conversion, directory operations, htree indexing, checksums, and vnode operations.

Key responsibilities:
- Export block/inode allocation, freeing, mapping, truncation, and update functions.
- Export directory lookup, readdir, insertion, deletion, rewrite, emptiness, and path-check functions.
- Export HTree lookup/add/create/hash helpers.
- Export checksum functions for superblocks, extattrs, directories, htree nodes, extents, bitmaps, inodes, and group descriptors.
- Export group descriptor accessors and sparse-superblock helpers.
- Define low-level block allocation flags.

Important definitions:
- Allocation/mapping prototypes: `ext2_alloc`, `ext2_balloc`, `ext2_blkfree`, `ext2_blkpref`, `ext2_bmap`, `ext4_bmapext`, `ext2_bmap_seekdata`.
- Inode lifecycle/conversion prototypes: `ext2_ei2i`, `ext2_i2ei`, `ext2_truncate`, `ext2_update`, `ext2_valloc`, `ext2_vfree`, `ext2_inactive`, `ext2_reclaim`.
- Directory/HTree prototypes: `ext2_lookup`, `ext2_readdir`, `ext2_htree_*`.
- Checksum prototypes: `ext2_sb_csum_*`, `ext2_extattr_blk_csum_*`, `ext2_dirent_csum_*`, `ext2_dx_csum_*`, `ext2_extent_blk_csum_*`, bitmap/inode/group descriptor checksum helpers.
- `BA_CLRBUF`, `BA_SEQMASK`, `BA_SEQSHIFT`, `BA_SEQMAX`.

Important interactions:
- Serves as the main private header connecting the ext2fs implementation units in this group with lookup, vnode, mount, and subr files outside this group.
