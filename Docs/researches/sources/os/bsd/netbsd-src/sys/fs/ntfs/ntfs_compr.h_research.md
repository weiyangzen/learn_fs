# File Research: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_compr.h

Private kernel header for NTFS compression support.

Key contents:
- Rejects non-kernel inclusion.
- Defines:
  - `NTFS_COMPBLOCK_SIZE` as `0x1000`.
  - `NTFS_COMPUNIT_CL` as `16`.
- Declares `ntfs_uncompblock()` and `ntfs_uncompunit()`.

Role:
- Small internal interface between the NTFS attribute read path and the compression decoder.
