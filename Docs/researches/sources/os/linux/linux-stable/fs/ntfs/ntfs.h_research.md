# File Research: sources/os/linux/linux-stable/fs/ntfs/ntfs.h

`ntfs.h` is a central NTFS driver header. It pulls in volume, layout, and inode definitions; defines basic constants/macros; exposes global caches and operation tables; and declares cross-file helper APIs.

Key contents:
- Defines `pr_fmt` for NTFS logging.
- Defines `NTFS_DEF_PREALLOC_SIZE`, compression constants, block size constants, max name/label lengths, and case-sensitivity constants.
- Provides conversion macros and inline helpers between bytes, clusters, folio/page indexes, folio offsets, MFT record numbers, and sectors.
- Declares slab caches for NTFS names, inodes, attribute contexts, and index contexts.
- Declares VFS operation tables for address-space, file, directory, symlink, special, empty inode, and export operations.
- Defines `NTFS_SB()` to retrieve `struct ntfs_volume` from a VFS superblock.
- Declares driver-wide functions from compression, superblock, MST, Unicode/name, ioctl, upcase, and block-device I/O modules.
- Includes `ntfs_ffs()`, a local first-set-bit helper.

Design role:
- This file is the low-level integration header that most NTFS implementation files include.
- The conversion helpers are used heavily by MFT and runlist code to translate logical NTFS units to page-cache and block-device units.
