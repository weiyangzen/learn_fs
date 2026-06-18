# File Research: sources/os/linux/linux-stable/fs/btrfs/fs.c

## Purpose

Provides core Btrfs filesystem helpers shared across the subsystem: checksum type metadata and dispatch, supported block-size validation, exclusive operation state transitions, and feature flag mutation helpers for incompat and compat-ro superblock flags.

## Checksum Helpers

`btrfs_csums[]` maps checksum type IDs to digest sizes and names. Public helpers return a checksum size/name/count and compute full or incremental checksums:

- `btrfs_csum()` computes CRC32C, xxhash64, SHA-256, or BLAKE2b in one call.
- `btrfs_csum_init()`, `btrfs_csum_update()`, and `btrfs_csum_final()` provide streaming checksum contexts.
- CRC32C uses Btrfs' inverted on-disk format; xxhash64 is little-endian; SHA-256 and BLAKE2b write raw digest bytes.

The code assumes checksum type validation happened at mount time and uses `BUG()` for impossible defaults.

## Block Size Validation

`btrfs_supported_blocksize()` accepts 4K, `PAGE_SIZE`, and `BTRFS_MIN_BLOCKSIZE`. Under `CONFIG_BTRFS_EXPERIMENTAL`, larger-than-page block sizes are allowed except for highmem configurations, where large folio content cannot always be accessed safely and several features are not large-folio ready.

## Exclusive Operations

`btrfs_exclop_start()`, `btrfs_exclop_start_try_lock()`, `btrfs_exclop_start_unlock()`, `btrfs_exclop_finish()`, and `btrfs_exclop_balance()` coordinate mutually exclusive operations such as balance, device add/remove, replace, resize, and swap activation. State is protected by `fs_info->super_lock`; completion notifies sysfs.

## Feature Flag Mutation

`__btrfs_set_fs_incompat()`, `__btrfs_clear_fs_incompat()`, `__btrfs_set_fs_compat_ro()`, and `__btrfs_clear_fs_compat_ro()` update superblock feature flags under `super_lock`, log transitions, and set `BTRFS_FS_FEATURE_CHANGED` so user-visible feature state can be refreshed. These helpers back macros in `fs.h`, including those used by free-space tree creation/deletion.

## Integration Notes

This file is infrastructure rather than free-space-specific, but it directly supports this group through checksum helpers, feature flag updates for `FREE_SPACE_TREE`/`FREE_SPACE_TREE_VALID`, mount/block-size constraints, and `btrfs_fs_info` state conventions declared in `fs.h`.
