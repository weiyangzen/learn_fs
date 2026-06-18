# File Research: sources/os/linux/linux/fs/smb/client/cifsfs.h

## Purpose
`cifsfs.h` declares the CIFS/SMB VFS-facing functions, operation tables, filesystem types, helper macros, and version constants exported across the SMB client implementation.

## Main Contents
- `ROOT_I`: root inode number constant.
- `cifs_sillycounter`, `cifs_tmpcounter`: counters for temporary/silly-renamed names.
- `cifs_uniqueid_to_ino_t()`: squashes 64-bit server file ids into `ino_t` safely on 32-bit architectures.
- `cifs_set_time()` / `cifs_get_time()`: dentry timestamp storage through `d_fsdata`.
- Extern declarations for:
  - filesystem types,
  - address-space operations,
  - inode operations,
  - file operations,
  - dentry operations,
  - export operations,
  - netfs request ops.
- VFS operation prototypes for create, lookup, mkdir, rename, getattr/setattr, fiemap, open/close, read/write, locks, fsync/flush, mmap, readdir, symlink, xattrs, ioctl, copychunk, and mount.

## Naming Constants
- `CIFS_TMPNAME_PREFIX` / `CIFS_TMPNAME_LEN`
- `CIFS_SILLYNAME_PREFIX` / `CIFS_SILLYNAME_LEN`

These support temporary files and silly rename behavior.

## Versioning
- `SMB3_PRODUCT_BUILD 60`
- `CIFS_VERSION "2.60"`

The comment notes these should be changed together.

## Role in the Group
This is the public local header for `cifsfs.c` and related VFS implementation files. It does not define complex state; that lives in `cifsglob.h`.
