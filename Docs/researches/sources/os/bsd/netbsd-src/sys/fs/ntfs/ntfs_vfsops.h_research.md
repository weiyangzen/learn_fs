# File Research: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_vfsops.h

Private NTFS VFS header.

Key contents:
- Rejects non-kernel inclusion.
- Declares:
  - `ntfs_vgetex()` for fetching vnodes by inode plus attribute type/name.
  - `ntfs_calccfree()` for free-cluster calculation from `$Bitmap`.

Role:
- Small bridge from NTFS helper/vnode code back into VFS-level functionality.
