# File Research: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_vfsops.c

Implements NTFS VFS operations, module registration, mounting, unmounting, root/stat operations, vnode loading, and file-handle conversion.

Key points:
- Module/VFS:
  - Defines `ntfs_vfsops` for `MOUNT_NTFS`.
  - Attaches malloc types, ntnode hash, and uppercase-table state during init.
  - Registers an NTFS sysctl node during module init.
- Mounting:
  - `ntfs_mount()` validates args, handles `MNT_GETARGS`, rejects updates, opens the block device, and calls `ntfs_mountfs()`.
  - `ntfs_mountfs()` invalidates old buffers, reads the boot block, validates NTFS signature and geometry, computes MFT record size, stores mount ownership/mode/flags, installs UTF-8 conversion hooks, and pins `$MFT`, root, and `$Bitmap` vnodes.
  - Loads `$UpCase`, computes free clusters from `$Bitmap`, and reads `$AttrDef` into internal attribute-definition records.
- Unmount:
  - Flushes non-system vnodes, checks pinned system vnode references, releases system vnodes, invalidates device buffers, closes the device, unuses `$UpCase`, and frees mount data.
- Vnode loading:
  - `ntfs_loadvnode()` takes an `ntkey`, loads the `ntnode` if needed, creates an `fnode`, fetches `$FILE_NAME` metadata, determines directory vs regular file, finds stream size/allocation, initializes genfs, and sets vnode identity.
  - `ntfs_vgetex()` creates vnode-cache keys that include inode, attribute type, and attribute name.
- Other operations:
  - Root lookup returns inode `NTFS_ROOTINO`.
  - `ntfs_calccfree()` scans `$Bitmap`.
  - `ntfs_statvfs()` reports space and file estimates.
  - `ntfs_fhtovp()` and `ntfs_vptofh()` preserve inode and attribute identity.

Risk/notes:
- Mount update is unsupported.
- System vnodes are deliberately pinned to keep core NTFS metadata accessible.
