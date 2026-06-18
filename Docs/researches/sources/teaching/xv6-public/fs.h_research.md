# File Research: sources/teaching/xv6-public/fs.h

Defines xv6’s on-disk filesystem format.

Contents:
- Root inode number and block size.
- `struct superblock` with filesystem size, data blocks, inode count, log start/size, inode start, and bitmap start.
- Direct/indirect block constants: `NDIRECT`, `NINDIRECT`, `MAXFILE`.
- `struct dinode` on-disk inode metadata and addresses.
- Inode/block bitmap helper macros `IPB`, `IBLOCK`, `BPB`, and `BBLOCK`.
- Directory entry size and `struct dirent`.

Shared by:
- Kernel filesystem code and host-side `mkfs`.
