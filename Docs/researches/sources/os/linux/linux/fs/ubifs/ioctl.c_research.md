# File Research: sources/os/linux/linux/fs/ubifs/ioctl.c

## Purpose

`ioctl.c` implements UBIFS support for ext2-compatible file attribute operations and fscrypt ioctls. It bridges persistent UBIFS inode flags, VFS inode flags, generic `fileattr` get/set APIs, and encryption policy/key ioctl dispatch.

## Flag Mapping

The file defines two masks. `UBIFS_SETTABLE_IOCTL_FLAGS` includes compression, sync, append-only, immutable, and directory-sync flags. `UBIFS_GETTABLE_IOCTL_FLAGS` adds encryption reporting. `ioctl2ubifs()` maps user-visible `FS_*` flags to `UBIFS_*` inode flags, while `ubifs2ioctl()` maps persistent UBIFS flags back to `FS_*` values and reports encrypted files through `FS_ENCRYPT_FL`.

`ubifs_set_inode_flags()` propagates UBIFS inode flags into `inode->i_flags`, clearing and then setting `S_SYNC`, `S_APPEND`, `S_IMMUTABLE`, `S_DIRSYNC`, and `S_ENCRYPTED`. This function is used after flag changes and during inode setup elsewhere in UBIFS.

## File Attribute Get/Set

`ubifs_fileattr_get()` rejects special dentries with `-ENOTTY`, converts UBIFS flags to generic fileattr flags, and fills the caller's `file_kattr`.

`ubifs_fileattr_set()` rejects special dentries, FS_X-style attributes, and unsupported flags. It masks input down to settable flags and removes `FS_DIRSYNC_FL` for non-directories. Actual persistence happens in `setflags()`.

`setflags()` budgets for a dirtied inode, locks the UBIFS inode mutex, replaces only settable UBIFS flag bits, updates VFS inode flags, sets ctime, and marks the inode dirty synchronously. If the inode was already dirty, it releases the just-reserved budget because existing dirty-inode budget covers the eventual write. If the inode is synchronous, it calls `write_inode_now()`.

## Encryption Ioctls

`ubifs_ioctl()` handles fscrypt policy, key-management, key-status, and nonce ioctls. Setting an encryption policy first calls `ubifs_enable_encryption(c)` so the filesystem feature state is enabled before delegating to fscrypt. Unsupported commands return `-ENOTTY`.

When `CONFIG_COMPAT` is enabled, `ubifs_compat_ioctl()` accepts the same fscrypt commands, converts the userspace pointer through `compat_ptr()`, and delegates to `ubifs_ioctl()`. Other compat commands return `-ENOIOCTLCMD`.

## Dependencies and Invariants

This file depends on VFS fileattr helpers, fscrypt ioctl helpers, UBIFS budgeting, UBIFS inode dirty accounting, and writeback. It intentionally does not allow userspace to set the encryption flag via generic attribute changes; encryption is reported but controlled through fscrypt policy ioctls.
