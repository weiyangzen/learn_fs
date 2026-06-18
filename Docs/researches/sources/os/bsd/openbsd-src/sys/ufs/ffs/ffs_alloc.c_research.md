# File Research: sources/os/bsd/openbsd-src/sys/ufs/ffs/ffs_alloc.c

Implements FFS block, fragment, inode, cylinder-group, and cluster allocation/freeing policy.

Key entry points:
- `ffs_alloc()` allocates blocks/fragments with minfree and quota enforcement.
- `ffs_realloccg()` grows an existing fragment in place or relocates it.
- `ffs_inode_alloc()` selects and allocates a new inode.
- `ffs_dirpref()` chooses cylinder groups for new directories.
- `ffs1_blkpref()` and `ffs2_blkpref()` choose preferred block locations for UFS1/UFS2.
- `ffs_hashalloc()` tries preferred cylinder group, quadratic rehash, then brute-force scan.
- `ffs_cgread()` reads and validates cylinder group blocks.
- `ffs_fragextend()`, `ffs_alloccg()`, and `ffs_alloccgblk()` allocate fragments/full blocks inside a cylinder group.
- `ffs_nodealloccg()` allocates an inode bitmap slot and lazily initializes UFS2 inode blocks.
- `ffs_blkfree()`, `ffs_inode_free()`, and `ffs_freefile()` return blocks/fragments/inodes to free maps.
- `ffs_mapsearch()` finds a free fragment pattern using `fragtbl`.
- `ffs_clusteracct()` maintains contiguous-cluster summaries.

Important behavior:
- Allocation respects quotas before committing disk space and rolls quota back on failure.
- Non-root users cannot consume below `fs_minfree`.
- Fragment growth switches between `FS_OPTSPACE` and `FS_OPTTIME` based on fragmentation pressure.
- Directory placement spreads top-level directories and limits too many consecutive directories in one cylinder group.
- Indirect block preferences reserve early data areas in a cylinder group for metadata locality.
- Freeing validates against double-free of blocks/fragments/inodes and panics on corruption for writable filesystems.

Dependencies:
- Uses FFS fragment tables from `ffs_tables.c`, bitmap helpers from `ffs_subr.c`, UFS quota helpers, buffer cache, and filesystem geometry macros.

Watch points:
- Many corruption cases intentionally panic, reflecting kernel filesystem invariant enforcement rather than defensive recovery.
- `ffs_cgread()` returning NULL causes allocation/free routines to fail quietly in several paths.
