# File Research: sources/os/linux/linux/fs/ntfs/ntfs.h

Top-level NTFS driver header.

Defines:
- Common includes and `pr_fmt`.
- Defaults and constants: `NTFS_DEF_PREALLOC_SIZE`, `STANDARD_COMPRESSION_UNIT`, `MAX_COMPRESSION_CLUSTER_SIZE`, `NTFS_BLOCK_SIZE`, `NTFS_SB_MAGIC`, max name/label lengths.
- Case comparison constants: `CASE_SENSITIVE`, `IGNORE_CASE`.
- Byte/cluster/MFT/folio/sector conversion macros and inline equivalents.

Exports:
- Slab caches for names, inodes, big inodes, attribute contexts, and index contexts.
- Address-space, file, inode, directory, empty-file, and export operation tables.
- `NTFS_SB()` accessor.
- Compression, superblock, MST, Unicode, ioctl, upcase, and block-device I/O function declarations.

Utility:
- `ntfs_ffs()` implements a local find-first-set helper.

Role:
- This header is the shared dependency surface for the NTFS driver files in this group, especially `mft.c`, `mst.c`, `namei.c`, `reparse.c`, and `runlist.c`.
