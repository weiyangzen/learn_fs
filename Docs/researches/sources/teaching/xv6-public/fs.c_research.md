# File Research: sources/teaching/xv6-public/fs.c

Implements xv6’s on-disk filesystem core: block allocation, inode cache, inode I/O, directories, and pathname traversal.

Key behavior:
- Reads the superblock and maintains a single global `sb`.
- `balloc` scans bitmap blocks, marks a free block allocated, logs bitmap updates, and zeroes the new block.
- `bfree` clears bitmap bits and panics on double-free.
- Maintains `icache` of `NINODE` in-memory inodes under spinlock plus per-inode sleeplocks.
- `ialloc`, `iget`, `idup`, `ilock`, `iunlock`, `iput`, and `iupdate` implement inode lifecycle and write-through disk metadata.
- `bmap` maps logical file blocks through 12 direct blocks and one indirect block, allocating as needed.
- `itrunc` frees all direct and indirect data blocks and updates inode size.
- `readi`/`writei` handle regular files and device inodes through `devsw`.
- `dirlookup` and `dirlink` implement fixed-size directory entries.
- `namex`, `namei`, and `nameiparent` parse slash-separated paths, handling absolute paths from root and relative paths from `cwd`.

Important interactions:
- Many operations assume the caller holds filesystem transaction context when `iput` may free disk state.
- Directory names are fixed `DIRSIZ` bytes and may be truncated by `skipelem`.
- The file only supports direct plus single-indirect addressing.
