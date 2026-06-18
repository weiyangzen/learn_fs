# File Research: sources/teaching/xv6-riscv/kernel/fs.h

Defines the on-disk filesystem format shared by kernel and `mkfs`.

Contents:
- `ROOTINO`, `BSIZE`, and disk layout comments.
- `struct superblock` describing total size, data block count, inode count, log layout, inode start, and bitmap start.
- `FSMAGIC`.
- File addressing constants: `NDIRECT`, `NINDIRECT`, `MAXFILE`.
- `struct dinode`, the on-disk inode format.
- Addressing macros: `IPB`, `IBLOCK`, `BPB`, `BBLOCK`.
- Directory format: `DIRSIZ` and `struct dirent`.

Filesystem relevance: this is the filesystem ABI. Both kernel `fs.c` and host-side `mkfs.c` must agree exactly on these structures and constants.
