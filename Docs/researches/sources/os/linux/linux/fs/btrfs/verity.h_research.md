# File Research: sources/os/linux/linux/fs/btrfs/verity.h

## Purpose

`verity.h` declares the Btrfs fs-verity interface and provides stubs when `CONFIG_FS_VERITY` is disabled.

## CONFIG_FS_VERITY Enabled

When fs-verity support is compiled in, the header includes `<linux/fsverity.h>` and exposes:

- `btrfs_verityops`, the `struct fsverity_operations` instance implemented in `verity.c`.
- `btrfs_drop_verity_items()`, used to remove descriptor and Merkle metadata.
- `btrfs_get_verity_descriptor()`, used to retrieve the fs-verity descriptor for an inode.

## CONFIG_FS_VERITY Disabled

When fs-verity is not compiled in:

- `btrfs_drop_verity_items()` is an inline no-op returning 0.
- `btrfs_get_verity_descriptor()` returns `-EPERM`.

This lets common Btrfs code call cleanup and descriptor helpers without open-coding configuration checks everywhere.

## Filesystem Role

The header is the compile-time boundary for Btrfs fs-verity support. It keeps optional verity code isolated while preserving stable call sites for the rest of the filesystem.
