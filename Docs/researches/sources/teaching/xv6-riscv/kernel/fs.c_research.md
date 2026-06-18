# File Research: sources/teaching/xv6-riscv/kernel/fs.c

Implements xv6’s filesystem layers: superblock reading, block allocation, inode cache, inode content, directories, and path lookup.

Important behavior:
- `fsinit()` reads and validates the superblock, initializes the log, and reclaims orphaned inodes.
- `balloc()` and `bfree()` manage bitmap-backed block allocation.
- `ialloc()`, `iget()`, `idup()`, `ilock()`, `iupdate()`, `iput()`, and `iunlock*()` manage disk and in-memory inode lifecycle.
- `ireclaim()` scans for allocated inodes with zero links at boot and forces normal `iput()` cleanup.
- `bmap()` maps logical file blocks to disk blocks, allocating direct or single-indirect blocks as needed.
- `itrunc()` frees all direct and indirect blocks and updates inode size.
- `readi()` and `writei()` perform inode data transfer through the buffer cache and log.
- Directory helpers implement fixed-size directory entries and name comparison.
- `namex()`, `namei()`, and `nameiparent()` implement absolute/relative path traversal with careful inode lock/ref handling.

Filesystem relevance: this is the core local filesystem implementation. It demonstrates xv6’s simple Unix-style inode filesystem with a bitmap allocator, direct plus single-indirect addressing, logged metadata/data updates, and directory-as-file semantics.
