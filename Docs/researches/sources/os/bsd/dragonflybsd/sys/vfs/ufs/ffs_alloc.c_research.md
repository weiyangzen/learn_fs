# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_alloc.c

FFS block, fragment, cluster, and inode allocation/free implementation for UFS.

Key responsibilities:
- Implements `ffs_alloc`, the top-level data block/fragment allocator. It validates sizes, enforces minfree for non-root users, charges quotas, selects a cylinder group from preference or inode location, calls the hash allocator, updates inode block counts, and reports full filesystems.
- Implements `ffs_realloccg`, growing a fragment in place when possible or relocating it through normal allocation, with `FS_OPTSPACE`/`FS_OPTTIME` switching based on fragmentation pressure.
- Provides sysctls under `vfs.ffs` for asynchronous free behavior and cluster reallocation behavior.
- Implements `ffs_reallocblks`, which tries to relocate a logical cluster of full blocks to a contiguous physical cluster, updates direct or indirect block maps, integrates soft updates dependencies, writes modified metadata, and frees old blocks.
- Implements `ffs_valloc`, selecting and allocating a new inode, then returning the corresponding vnode through `VFS_VGET`.
- Implements `ffs_dirpref`, choosing cylinder groups for new directories using root-level spreading, average free inode/block thresholds, maximum contiguous-directory heuristics, and parent locality.
- Implements `ffs_blkpref`, computing preferred block placement based on direct/indirect section boundaries, average free blocks, previous allocations, max contiguous blocks, and rotational delay.
- Implements `ffs_hashalloc`, the shared preferred-CG, quadratic-rehash, and brute-force fallback allocator loop used for blocks, clusters, and inodes.
- Implements internal allocation helpers: `ffs_fragextend`, `ffs_alloccg`, `ffs_alloccgblk`, `ffs_clusteralloc`, `ffs_nodealloccg`, and `ffs_mapsearch`.
- Implements `ffs_blkfree_cg`, returning blocks/fragments to cylinder-group maps, reassembling fragments into full blocks, updating free summaries and cluster accounting.
- Implements TRIM-aware `ffs_blkfree`, issuing `BUF_CMD_FREEBLKS` when mounted with `MNT_TRIM` and deferring bitmap free until the device callback schedules `ffs_blkfree_trim_task`.
- Implements diagnostic `ffs_checkblk` for allocation-state verification.
- Implements `ffs_vfree` and `ffs_freefile`, freeing inodes directly or via soft updates.
- Implements `ffs_clusteracct`, maintaining cluster free maps, cluster summaries, and `fs_maxcluster`.
- Implements `ffs_fserr`, logging filesystem/user error diagnostics.

Dependencies:
- Uses DragonFly kernel buffer cache, vnode, mount, sysctl, taskqueue, BIO, device, quota, and soft updates APIs.
- Depends on UFS inode structures, `ufsmount`, filesystem layout macros from `fs.h`, and exported prototypes in `ffs_extern.h`.
- Integrates with quotas through `ufs_chkdq` and inode hash avoidance through `ufs_ihashcheck`.

Notable risks:
- This is core metadata mutation code; incorrect bitmap, summary, quota, or soft updates ordering can corrupt filesystems.
- Many paths panic on detected internal inconsistency, as expected for kernel metadata corruption checks.
- TRIM free ordering is intentionally delayed to avoid reusing blocks before trim completes; callback pointer handling and taskqueue scheduling are sensitive.
- Allocation decisions depend on legacy rotational geometry fields that may be approximate on modern storage.
- Inode allocation deliberately avoids inodes still present in the hash, handling races with vnode reclamation.
- Cluster reallocation spans direct and indirect block maps and has complex cleanup semantics when allocation fails.
