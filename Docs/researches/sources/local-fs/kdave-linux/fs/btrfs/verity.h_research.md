# File Research: sources/local-fs/kdave-linux/fs/btrfs/verity.h

## Purpose

`verity.h` declares Btrfs fs-verity integration points and provides configuration-dependent stubs when fs-verity is disabled.

## CONFIG_FS_VERITY Enabled

When `CONFIG_FS_VERITY` is enabled, the header includes `<linux/fsverity.h>` and declares:

- `extern const struct fsverity_operations btrfs_verityops`
- `btrfs_drop_verity_items()`
- `btrfs_get_verity_descriptor()`

These are implemented in `verity.c` and used by Btrfs inode and cleanup paths.

## CONFIG_FS_VERITY Disabled

When fs-verity support is disabled, the header provides inline stubs:

- `btrfs_drop_verity_items()` returns `0`, making cleanup callers harmless.
- `btrfs_get_verity_descriptor()` returns `-EPERM`, preventing descriptor access without fs-verity support.

## Integration Notes

The header forward-declares `struct inode` and `struct btrfs_inode`, keeping dependencies minimal. It is the compile-time switch point that lets the rest of Btrfs call verity cleanup/access helpers without open-coding `#ifdef CONFIG_FS_VERITY` at every call site.
