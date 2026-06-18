# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ffs/inode.c

Implements FFS/UFS inode traversal, inode-buffered reads, directory inode caching, inode clearing, allocation, and diagnostics.

Traversal:
- `ckinode` walks direct and indirect block pointers for a UFS1/UFS2 inode.
- It skips device inodes and short symlinks that store data inline.
- It computes fragment counts for final direct blocks and dispatches either block callbacks or directory scans.
- It detects empty directory blocks and can adjust directory length while requesting a rerun.
- `iblock` recursively traverses indirect blocks, handles UFS1/UFS2 indirect entry widths, clears partially truncated entries when allowed, and descends through directory/data callbacks.

Validation and access:
- `chkrange` verifies positive block ranges, fragment alignment, fragment count, and cylinder group metadata/data bounds.
- `ginode` reads the inode block containing a specific inode.
- `getnextinode`, `setinodebuf`, and `freeinodebuf` implement sequential buffered inode reads for pass 1.

Directory inode cache:
- `cacheino` records directory inode size, parent/dotdot placeholders, and direct/indirect block addresses.
- `getinoinfo` looks cached directories up by hash.
- `inocleanup` frees directory cache structures.

Repair helpers:
- `clri` clears an inode and releases its blocks.
- `findname` and `findino` support pathname reconstruction and directory lookup.
- `pinode` prints owner, mode, size, and mtime.
- `blkerror` marks inodes for clearing after bad or duplicate block discovery.
- `allocino` allocates a free inode, extends per-cylinder-group state arrays if needed, updates cylinder group inode bitmap/counts, allocates an initial data block, initializes ownership/times/mode, and sets inode state/type.
- `freeino` releases blocks and clears inode state.

This file is the FFS checker’s core inode and block-walk layer, with explicit support for both UFS1 and UFS2 metadata formats.
