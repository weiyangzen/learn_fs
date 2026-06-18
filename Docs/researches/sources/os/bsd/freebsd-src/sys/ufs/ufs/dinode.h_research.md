# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/dinode.h

## Purpose
Defines the UFS on-disk inode formats and associated constants for UFS1 and UFS2.

## Key Contents
- Special inode numbers:
  - `UFS_ROOTINO` is inode 2.
  - `UFS_WINO` is inode 1, used as the whiteout placeholder.
- Core on-disk types:
  - `ufs1_daddr_t`
  - `ufs2_daddr_t`
  - `ufs_lbn_t`
  - `ufs_time_t`
- Mode and permission bits:
  - `IEXEC`, `IWRITE`, `IREAD`, `ISVTX`, `ISGID`, `ISUID`
- File type bits:
  - `IFMT`, `IFIFO`, `IFCHR`, `IFDIR`, `IFBLK`, `IFREG`, `IFLNK`, `IFSOCK`, `IFWHT`
- Block pointer constants:
  - `UFS_NXADDR`
  - `UFS_NDADDR`
  - `UFS_NIADDR`
- `struct ufs2_dinode`:
  - 64-bit size/block/time fields.
  - UID/GID, mode, link count, flags, generation, block size.
  - Birth time and nanosecond timestamps.
  - External attribute blocks via `di_extb`.
  - Direct/indirect block arrays or embedded short symlink union.
  - `di_modrev`, SUJ freelink or directory depth, inode checksum.
- `struct ufs1_dinode`:
  - Legacy UFS1 layout with 32-bit disk block addresses and timestamp seconds.
  - Direct/indirect block arrays or embedded short symlink union.
  - UID/GID, flags, generation, block count, `di_modrev`.
- Overlay:
  - `di_rdev` maps device number onto first direct block.
- Limits/unions:
  - `UFS_LINK_MAX`
  - `union dinode`
  - `union dinodep`

## Interactions
- Included by `inode.h` for in-core inode access.
- Included by `ffs/fs.h` for filesystem geometry and block/inode macros.
- The `DIP`/`DIP_SET` macros in `inode.h` abstract over UFS1 vs UFS2 fields.
