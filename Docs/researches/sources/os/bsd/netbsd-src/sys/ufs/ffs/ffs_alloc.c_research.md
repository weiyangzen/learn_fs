# File Research: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_alloc.c

This file implements FFS block, fragment, inode allocation and free logic, including cylinder-group policies, quota checks, WAPBL integration, snapshot variants, and discard/TRIM batching.

Key responsibilities:
- Allocate data blocks/fragments and inodes.
- Reallocate fragments as files grow.
- Choose preferred blocks and cylinder groups for locality.
- Maintain cylinder-group summaries, fragment summaries, cluster accounting, inode bitmaps, and filesystem totals.
- Free blocks/fragments and inodes, including snapshot-specific paths.
- Batch optional block discard operations.
- Report filesystem-full and out-of-inode errors.

Important allocation functions:
- `ffs_check_bad_allocation`: Validates block/fragment size, alignment, fragment boundary containment, and filesystem range.
- `ffs_alloc`: Allocates a block/fragment under `um_lock`, checks reserved space and quotas, chooses starting cylinder group, calls `ffs_hashalloc`, updates inode block count and flags, or reports ENOSPC.
- `ffs_realloccg`: Grows an existing fragment. It first tries `ffs_fragextend`; if that fails, it allocates a new location, copies/grows the buffer, frees the old fragment, updates quotas and inode block count, and handles optimization mode changes between `FS_OPTSPACE` and `FS_OPTTIME`.
- `ffs_valloc`: Allocates an inode under WAPBL. Directory allocations use `ffs_dirpref`; non-directories prefer the parent cylinder group. Updates `fs_contigdirs` tracking.
- `ffs_dirpref`: Selects a cylinder group for a new directory using average free inode/block counts, directory distribution, parent/root behavior, and contiguous-directory limits.
- `ffs_blkpref_ufs1` and `ffs_blkpref_ufs2`: Compute preferred block addresses for UFS1/UFS2 direct/indirect allocations, including contiguous-file hints via inode extension fields.
- `ffs_hashalloc`: Tries the preferred cylinder group, then quadratic rehash, then brute-force cylinder group search.
- `ffs_fragextend`: Checks adjacent free fragments and extends an allocated fragment in place, updating fragment summaries and free counts.
- `ffs_alloccg`: Allocates a block or fragment within a cylinder group. Full-block allocation delegates to `ffs_alloccgblk`; fragment allocation may split a full block.
- `ffs_alloccgblk`: Allocates a full block from a cylinder group, preferring the requested block, otherwise using map search and updating block, cluster, and old rotational accounting.
- `ffs_nodealloccg`: Allocates an inode in a cylinder group, lazily initializes UFS2 inode blocks when necessary, registers the inode with WAPBL, updates bitmaps and directory counts.

Important free and discard functions:
- `ffs_blkalloc` and `ffs_blkalloc_ump`: Explicitly reserve a specific block/fragment if currently free, updating free maps and summaries.
- `ffs_blkfree`: Frees a block/fragment, handles snapshots via `ffs_snapblkfree`, validates the allocation, and either frees immediately or batches discard work.
- `ffs_blkfree_cg`: Reads the cylinder group and delegates to common free logic for normal device vnodes.
- `ffs_blkfree_snap`: Snapshot variant that reads cylinder group data through the snapshot vnode.
- `ffs_blkfree_common`: Common bitmap and accounting update for freeing blocks/fragments, including fragment reassembly into full blocks and double-free panics for non-snapshot paths.
- `ffs_discard_init`, `ffs_discard_finish`, `ffs_discardcb`, `ffs_blkfree_td`: Manage deferred discard/TRIM operations and then perform actual filesystem free operations under WAPBL transactions.
- `ffs_vfree`, `ffs_freefile`, `ffs_freefile_snap`: Free inodes in normal or snapshot contexts.
- `ffs_freefile_common`: Clears inode bitmap, unregisters WAPBL inode for non-snapshot paths, updates rotor, free inode counts, and directory counts.
- `ffs_checkfreefile`: Tests whether an inode is free in a snapshot cylinder group.
- `ffs_mapsearch`: Searches a cylinder-group free-block bitmap for a fragment pattern of the requested size and panics if summaries claim availability but the map is corrupt.
- `ffs_fserr`: Logs filesystem errors with uid/pid/command context.

Important interactions:
- Used by FFS block allocation in `ffs_balloc.c`, inode creation paths, truncation/free paths, snapshots, WAPBL journaling, quota code, and optional discard support.
- Requires careful `um_lock` discipline: many routines enter with `um_lock` held and release it on success, while lower allocator callbacks may release on success and retain on failure as documented in comments.
- UFS1/UFS2 byte swapping is handled through `ufs_rw*` helpers and `UFS_FSNEEDSWAP`.
- Snapshot and WAPBL code affect whether frees are immediate, registered, or routed through snapshot copy handling.

Notable behavior and risks:
- Several allocation functions intentionally panic on inconsistent maps or impossible sizes, treating metadata corruption as fatal.
- `ffs_alloc` has special handling for `B_CONTIG` because lock ownership after failed contiguous allocation is described as suspect.
- `ffs_realloccg` uses forced deallocation registration for non-regular WAPBL cases because the code cannot handle registration failure there.
- Discard batching coalesces backward frees up to a fixed `maxsize` of 100 KiB before enqueueing work.
