# File Research: sources/os/linux/linux-stable/fs/smb/client/cifsfs.h

Read status: complete.

## Purpose

Declares CIFS VFS-facing operations, helpers, filesystem types, file operation tables, and module version constants shared by the client implementation.

## Main Contents

- `ROOT_I`
  - Root inode number constant.

- `cifs_uniqueid_to_ino_t()`
  - Converts a 64-bit server file id to `ino_t`.
  - Hashes down to a nonzero 31-bit value on 32-bit `ino_t` platforms.

- Dentry time helpers:
  - `cifs_set_time()`
  - `cifs_get_time()`

- Extern declarations for:
  - `cifs_fs_type`
  - `smb3_fs_type`
  - address-space operations
  - inode operations
  - file operations
  - dentry operations
  - export operations when enabled

- VFS operation prototypes:
  - create/open/tmpfile/lookup/unlink/link/mkdir/rmdir/rename/mknod
  - revalidation
  - getattr/setattr/fiemap
  - file read/write/fsync/flush/lock/mmap/readdir
  - symlink handling
  - xattr listing
  - copychunk, ioctl, setsize, mount

- Temporary and silly rename name prefixes:
  - `CIFS_TMPNAME_PREFIX`
  - `CIFS_SILLYNAME_PREFIX`

- Version constants:
  - `SMB3_PRODUCT_BUILD`
  - `CIFS_VERSION`

## Role in the Subsystem

This is the public local header for CIFS VFS integration. It binds together declarations implemented across `cifsfs.c`, inode/file/dir/xattr modules, and mount code.
