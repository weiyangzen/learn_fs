# File Research: sources/os/linux/linux-stable/fs/affs/affs.h
- Purpose: Central private header for AFFS.
- Main types: `affs_inode_info`, `affs_bm_info`, `affs_sb_info`, and extension/cache structures for file block metadata.
- On-disk helpers: Defines macros for AFFS block headers, tails, root blocks, data blocks, hash table slots, and data payloads.
- Mount state: Stores partition geometry, root block, hash size, uid/gid/mode overrides, bitmap state, root buffer, symlink prefix state, delayed superblock work, and mount flags.
- Declarations: Exposes hash/link helpers, checksum helpers, protection conversion, bitmap allocation/freeing, namei operations, inode/file/dir/symlink operation tables, and address-space ops.
- Inline helpers: Validate block numbers, read/get/zero buffers, adjust checksums, and lock/unlock inode link/hash/extension mutexes.
- Risks: Many helpers directly manipulate buffer_head-backed on-disk structures; locking discipline around link/hash/ext state is important.
