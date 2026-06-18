# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/inode.c

Implements ext2 inode traversal, inode cache management, inode allocation/freeing, and inode diagnostics.

Block traversal:
- `ckinode` walks direct and indirect block pointers for an inode, dispatching either block-address callbacks or directory scans.
- `iblock` recursively handles single/double/triple indirect blocks and clears partially truncated indirect entries when repairing.
- Empty directory blocks can trigger directory length adjustment and request a rerun.

Size and range handling:
- `inosize` reads 64-bit regular-file sizes using `e2di_size_hi`.
- `inossize` writes sizes and ensures large-file feature bits are set for large regular files.
- `setlarge` repairs the ext2 large-file rocompat feature when needed.
- `chkrange` validates block numbers against filesystem bounds and per-group metadata/data regions.

Inode access:
- `ginode` reads the inode block containing a requested inode.
- `getnextinode`, `resetinodebuf`, and `freeinodebuf` implement sequential buffered inode reading for pass 1.
- `cacheino`, `getinoinfo`, and `inocleanup` maintain the directory inode cache used by later passes.

Repair helpers:
- `clri` clears an inode and releases its blocks.
- `findname` and `findino` support pathname construction and directory lookup.
- `pinode` prints owner, mode, size, and mtime.
- `blkerror` marks file/directory state for duplicate or bad blocks.
- `allocino` creates a new inode and first block.
- `freeino` releases an inode through pass4 block cleanup.

This file is the core metadata traversal layer beneath ext2 fsck’s pass logic.
