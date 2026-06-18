# File Research: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_alloc.c

Main FFS allocation, free-space accounting, inode allocation, block reallocation, TRIM aggregation, cylinder-group integrity, and live fsck repair interface.

Key responsibilities:
- `ffs_alloc()` allocates fragments/blocks with quota charging, free-space reserve enforcement, preferred-cylinder selection, softdep cleanup retry, fsfail handling, inode block count updates, and full-filesystem diagnostics.
- `ffs_realloccg()` grows a fragment in place when possible, otherwise allocates a replacement block/fragment, copies/zeros buffer state, frees the old allocation, and switches between space/time optimization.
- `ffs_reallocblks()` plus UFS1/UFS2 variants tries to relocate logical block clusters into contiguous physical extents, updating inode or indirect pointers, coordinating softdep dependencies, then freeing old blocks.
- `ffs_valloc()` allocates a new inode, using `ffs_dirpref()` for directories, `ffs_hashalloc()` for cylinder-group fallback, vnode replacement through `ffs_vgetf()`, generation number initialization, UFS1/UFS2 vnode op selection, and inode birthtime initialization for UFS2.
- `ffs_dirpref()` spreads high-level directories while clustering deeper related directories, using directory depth, average free inode/block counts, existing directory counts, and `fs_contigdirs`.
- `ffs_blkpref_ufs1()` and `ffs_blkpref_ufs2()` compute placement preferences for direct data, indirect metadata, directory blocks, first indirect/data locality, max-blocks-per-cylinder-group sections, and average-free-block cylinder selection.
- `ffs_hashalloc()` implements preferred-cylinder allocation, quadratic rehash, then brute-force cylinder-group search.
- `ffs_fragextend()`, `ffs_alloccg()`, `ffs_alloccgblk()`, `ffs_clusteralloc()`, and `ffs_mapsearch()` operate directly on cylinder-group bitmaps, fragment summaries, block summaries, cluster summaries, and rotors.
- `ffs_nodealloccg()` allocates inodes from cylinder-group inode maps and initializes new UFS2 inode blocks with barrier or synchronous writes before exposing them in the inode map.
- `ffs_blkfree()` and `ffs_blkfree_cg()` free blocks/fragments, handle snapshots/copy-on-write, update block/fragment/cluster summaries, integrate softdep free dependencies, and detect double frees.
- TRIM support (`ffs_blkrelease_start()`, `ffs_blkrelease_finish()`, `trim_lookup()`, `ffs_blkfree_sendtrim()`) consolidates contiguous freed block ranges and delays bitmap reuse until BIO_DELETE completion.
- `ffs_freefile()`, `ffs_vfree()`, and `ffs_checkfreefile()` manage inode bitmap frees and snapshot checks.
- `ffs_getcg()` reads and validates cylinder groups, including CRC/check-hash verification, magic/cg number checks, background-write flags, and timestamp update policy.
- `ffs_checkcgintegrity()` quarantines a corrupt cylinder group by zeroing its summary resources, clearing maxcluster, and marking the filesystem `FS_NEEDSFSCK`.
- `sysctl_ffs_fsck()` exposes controlled live repair commands for fsck: adjust inode ref/block/depth, set size, adjust superblock summaries, free inode/block ranges, set flags, set cwd, rewrite `..`, and unlink duplicate names.

Important patterns:
- UFS mount lock protects global summary mutations; cylinder-group buffers are read/modified around deliberate lock drops.
- Allocation paths commonly retry after `softdep_request_cleanup()` before reporting `ENOSPC`.
- Soft updates are wired into every allocation/free map mutation via setup functions instead of being an afterthought.
- TRIM is conservative: blocks are not returned to free maps until delete I/O completes, preventing reuse-before-delete reordering.
- Integrity failures avoid repeated bad-cylinder use by modifying summary state in memory and forcing fsck.

Research relevance:
- This is the central policy and bitmap implementation for FFS free-space management.
- It explains FFS locality heuristics, fragmentation policy, soft updates integration, quota interaction, snapshots, TRIM behavior, and online fsck repair hooks.
