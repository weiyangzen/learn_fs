# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_vfsops.c

This file implements the NTFS VFS layer: mount, unmount, root lookup, statfs/statvfs, vnode lookup by inode, NFS filehandle conversion, export checking, and module initialization. It defines NTFS malloc types and the global `ntfs_iconv` function table pointer.

`ntfs_mount()` handles root and non-root mounts, argument copyin, update/export handling, device lookup, and device validation. `ntfs_mountfs()` opens the block device, reads and validates the boot sector, computes MFT record size, initializes charset tables, installs vnode ops, opens retained system vnodes (`$MFT`, root, `$Bitmap`), loads `$UpCase`, counts free clusters from `$Bitmap`, and reads `$AttrDef` into internal translated definitions.

`ntfs_unmount()` flushes non-system and system vnodes, checks retained system vnode references, closes the device, releases charset/toupper state, frees attribute definitions and mount state, and clears `MNT_LOCAL`.

`ntfs_vgetex()` is the central vnode factory. It maps inode number plus attribute type/name to an `ntnode` and `fnode`, optionally loads attributes, computes vnode type and stream size, reuses an existing vnode if present, otherwise allocates and initializes a new vnode.

Research notes: mount setup is read-heavy and retains core metadata vnodes to keep access stable. Export support uses inode-number-only file handles, with comments noting limited mutation support.
