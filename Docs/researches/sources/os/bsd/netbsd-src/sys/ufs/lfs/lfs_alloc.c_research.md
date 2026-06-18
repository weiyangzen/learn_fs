# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_alloc.c

Read completely: 1153 lines.

Implements LFS inode allocation, fixed-number inode allocation, inode freeing, ifile extension, free-list reconstruction, orphan marking/recovery, and DEBUG free-list validation.

Core free-list model:
- Free inode state is stored in ifile entries using `if_daddr == LFS_UNUSED_DADDR` and `if_nextfree` links.
- A runtime bitmap mirrors free inode state for faster checks and diagnostics.
- Cleaner info carries free-list head/tail for newer LFS formats; compatibility macros update the appropriate storage.
- `LFS_ILLEGAL_DADDR` is used under DEBUG to distinguish allocated-but-not-yet-addressed inodes.

Main paths:
- `lfs_extend_ifile()` grows the ifile by one block, reallocates the inode bitmap, initializes new ifile entries, prepends new inodes to the free list, fixes tail when needed, and writes the new ifile block.
- `lfs_valloc()` allocates the free-list head, verifies the entry is free, updates the free-list head, records the generation/version, marks the inode allocated, extends the ifile when the list becomes empty, marks the filesystem modified, and increments file count.
- `lfs_valloc_fixed()` allocates a specific inode/version for roll-forward or recovery use, extending the ifile if necessary and unlinking the target inode from wherever it appears in the free list.
- `lfs_vfree()` waits for pending writes, removes dirop state, finalizes or transfers pending segment-use accounting, clears unwritten inode state, marks the inode deleted/free, clears the ifile disk address, bumps the version, reinserts it on the free list, marks the filesystem modified, and decrements file count.
- `lfs_order_freelist()` scans the full ifile at mount, rebuilds the sorted free list and bitmap, and records orphaned inodes for later reclamation.
- `lfs_orphan()` marks unlinked but still referenced files with the magic orphan nextfree value and may mark the inode dead if only internal references remain.
- `lfs_free_orphans()` vgets and vputs orphaned inodes found during mount so reclaim paths free them.

Debug support:
- `lfs_check_freelist()` verifies that free entries and the linked free list agree, detects loops, count mismatches, bad tail pointers, and in-use inodes on the free list.
- `dump_freelist()` prints free-list head, tail, and sample links for diagnostics.

Risks and notes:
- Corrupt ifile/free-list state commonly leads to `panic()`, not graceful repair.
- Several old ordered-free-list helpers are compiled out, and comments question why list insertion ordering was abandoned.
- Locking relies on preventative lock, fragment lock, vnode interlock, and global `lfs_lock`; many functions assert segment-lock expectations rather than proving them.
- Orphan handling comments acknowledge uncertainty about historical behavior but preserve the recovery mechanism.
