# File Research: sources/os/linux/linux-stable/fs/hfs/hfs_fs.h

## Scope

Primary classic HFS filesystem header. Defines in-memory inode/superblock state, flags, public helper prototypes, time conversion helpers, dirtying helpers, and 512-byte-sector block-read macro.

## Key Structures

- `struct hfs_inode_info` stores open count, flags, timezone offset, catalog key, open directory iterator list, resource-fork inode pointer, extent lock/cache, fork sizes, and embedded VFS inode.
- `struct hfs_sb_info` stores primary/alternate MDB buffers, allocation bitmap, extents/catalog B-trees, file/folder/CNID counters, allocation geometry, mount defaults, NLS tables, bitmap/MDB dirty state, delayed work state, and partition/session options.

## API Surface

The header exposes bitmap, catalog, directory, extent, inode, xattr, MDB, partition, string, translation, and superblock dirtying APIs. It also defines `HFS_I()`/`HFS_SB()` accessors, HFS timestamp conversion between Mac and Unix epochs with timezone adjustment, and `sb_bread512()` for sector-granular reads on larger block devices.

## Risks And Invariants

The timestamp model intentionally maps pre-1970 on-disk values into the 2040-2106 range to match historical 64-bit Linux behavior. Superblock dirty flags distinguish MDB, alternate MDB, and bitmap writes. Resource forks use a paired inode pointer and `HFS_FLG_RSRC`, so main/resource inode lifetime must stay synchronized.
