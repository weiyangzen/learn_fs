# File Research: sources/local-fs/btrfs-linux/fs/btrfs/ioctl.h

## Purpose

Declares the ioctl/fileattr interfaces exported from `ioctl.c` to the rest of Btrfs.

## Contents

- Main ioctl entry points: `btrfs_ioctl()` and `btrfs_compat_ioctl()`.
- File attribute handlers: `btrfs_fileattr_get()` and `btrfs_fileattr_set()`.
- Supported feature ioctl helper.
- Inode flag synchronization helper.
- Balance status argument updater.
- io_uring encoded command entry and encoded read endio callback.

## Dependencies

Uses forward declarations for VFS objects, Btrfs inode/fs structures, balance args, and `io_uring_cmd`, keeping this header lightweight.
