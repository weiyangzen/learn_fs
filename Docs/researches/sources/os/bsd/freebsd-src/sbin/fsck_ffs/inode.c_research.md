# File Research: sources/os/bsd/freebsd-src/sbin/fsck_ffs/inode.c

This file implements inode traversal, block reachability lookup, inode cache reads, block/inode freeing, snapshot copy-on-write preservation, directory inode cache management, and inode diagnostic helpers.

Key behavior:
- `ckinode()` walks an inode’s direct and indirect block tree and applies the descriptor callback, or `dirscan()` for directory data.
- `iblock()` recursively walks indirect blocks, detects partially truncated inodes, and clears invalid excess indirect pointers when allowed.
- `ino_blkatoff()` and `indir_blkatoff()` resolve logical block numbers, including negative lbn forms for extattrs and indirect blocks.
- `chkrange()` validates fragment ranges against filesystem size and cylinder group metadata/data boundaries.
- `ginode()` loads a specific inode, using the sequential pass-1 buffer or cached inode block, verifies UFS2 inode hashes, and performs old-format compatibility updates.
- `getnextinode()` is the optimized sequential reader used by pass 1 and pass 1b; it also helps detect valid inode extent during cylinder group rebuild.
- `setinodebuf()` configures sequential inode scanning for a cylinder group.
- `freeblock()` releases blocks, updates duplicate-block tracking, block map, counters, and cylinder group summaries.
- `snapremove()`, `snapclean()`, `snapblkfree()`, `copyonwrite()`, and `chkcopyonwrite()` preserve snapshot semantics when blocks are freed or overwritten.
- `check_blkcnt()` recomputes and repairs inode `di_blocks`.
- `cacheino()`, `getinoinfo()`, `removecachedino()`, and `inocleanup()` maintain directory metadata caches for passes 2 and 3.
- `inodirty()` updates UFS2 inode check hashes before marking inode buffers dirty.
- `clri()` clears an inode and frees its blocks, with special handling for snapshots and background sysctl adjustment.
- `findname()`, `findino()`, and `clearentry()` are directory-scan callbacks.
- `prtinode()` prints owner, mode, size, and mtime.
- `blkerror()` marks inodes for clearing after bad or duplicate block discovery.
- `allocino()` and `freeino()` allocate/deallocate inodes and their initial block.

Important invariants:
- Snapshot blocks must be claimed or copied before a live block is freed/overwritten.
- Direct blocks in snapshots are assumed pre-copied.
- UFS2 inode check hashes are updated on dirtying and repaired on read when accepted.
- `ckinode()` treats embedded symlinks and special devices as not having normal data blocks.
