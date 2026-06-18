# File Research: sources/os/linux/linux-stable/fs/ubifs/ioctl.c

## Role

Implements UBIFS file attribute flag handling and fscrypt ioctl dispatch. The file provides EXT2-compatible flag translation for VFS file attributes and forwards encryption ioctls to fscrypt.

## Inode Flag Mapping

`ubifs_set_inode_flags()` propagates persistent UBIFS inode flags into VFS `i_flags`:

- `UBIFS_SYNC_FL` to `S_SYNC`
- `UBIFS_APPEND_FL` to `S_APPEND`
- `UBIFS_IMMUTABLE_FL` to `S_IMMUTABLE`
- `UBIFS_DIRSYNC_FL` to `S_DIRSYNC`
- `UBIFS_CRYPT_FL` to `S_ENCRYPTED`

`ioctl2ubifs()` maps settable fileattr flags to UBIFS flags. `ubifs2ioctl()` maps UBIFS flags back to generic fileattr flags and exposes encryption as `FS_ENCRYPT_FL`.

## Fileattr Operations

`ubifs_fileattr_get()` rejects special dentries, converts UBIFS flags, and fills `struct file_kattr`.

`ubifs_fileattr_set()` rejects special dentries, fsx-style attributes, and unsupported flags. It masks input to settable flags and disallows `FS_DIRSYNC_FL` on non-directories. Changes are applied through `setflags()`.

`setflags()` budgets inode dirtiness, updates `ui->flags` under `ui_mutex`, refreshes VFS flags, updates ctime, marks the inode dirty synchronously, releases unused budget if the inode was already dirty, and writes immediately for synchronous inodes.

## Encryption Ioctls

`ubifs_ioctl()` supports fscrypt operations:

- set/get encryption policy
- get extended policy
- add/remove keys
- remove keys for all users
- get key status
- get encryption nonce

Before setting an encryption policy it calls `ubifs_enable_encryption()`.

`ubifs_compat_ioctl()` forwards supported compat ioctls through `compat_ptr()` and rejects others with `-ENOIOCTLCMD`.

## Research Notes

This file is intentionally narrow: persistent flag mutation is journaled later through inode dirty writeback, while encryption-specific semantics are delegated to fscrypt after UBIFS enables encryption support.
