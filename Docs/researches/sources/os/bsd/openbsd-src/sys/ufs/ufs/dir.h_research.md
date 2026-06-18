# File Research: sources/os/bsd/openbsd-src/sys/ufs/ufs/dir.h

Read completely: 134 lines.

Defines UFS directory entry format and helper macros.

Core definitions:
- `doff_t` is a 32-bit directory offset, with `MAXDIRSIZE` capped near 2 GB.
- `DIRBLKSIZ` is `DEV_BSIZE`; entries are variable-length records inside fixed directory blocks.
- `struct direct` contains inode number, record length, type, name length, and a null-terminated name buffer up to `MAXNAMLEN`.
- Defines directory file type constants and conversion macros `IFTODT()` and `DTTOIF()`.
- `DIRECTSIZ()` and `DIRSIZ()` compute record sizes rounded to 4-byte boundaries.
- `struct dirtemplate` provides the packed `"."` and `".."` layout used for new directories and parent checks.

Integration and risks:
- Deletion and insertion rely on `d_reclen` absorbing free space.
- Directory readers must validate record lengths to avoid infinite loops and malformed entry exposure.
- The kernel tolerates some noncanonical free entries created by fsck.
