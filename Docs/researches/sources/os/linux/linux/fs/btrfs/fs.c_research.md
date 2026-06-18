# File Research: sources/os/linux/linux/fs/btrfs/fs.c

## Purpose
Provides shared Btrfs filesystem-level helpers: checksum dispatch, block-size validation, exclusive-operation state transitions, and superblock feature flag mutation.

## Checksum Support
- `btrfs_csums[]` maps checksum type to digest size and name:
  - CRC32C
  - XXHASH64
  - SHA256
  - BLAKE2b
- `btrfs_csum_type_size()`, `btrfs_super_csum_size()`, `btrfs_super_csum_name()`, and `btrfs_get_num_csums()` expose metadata.
- `btrfs_csum()` computes one-shot checksums.
- `btrfs_csum_init()`, `btrfs_csum_update()`, and `btrfs_csum_final()` provide streaming checksum API through `struct btrfs_csum_ctx`.
- Unknown checksum types hit `BUG()` because mount-time validation is expected to have rejected them.

## Block Size Validation
- `btrfs_supported_blocksize()` accepts common supported block sizes:
  - 4 KiB,
  - `PAGE_SIZE`,
  - `BTRFS_MIN_BLOCKSIZE`.
- Under `CONFIG_BTRFS_EXPERIMENTAL`, larger-than-page block sizes can be accepted except on `HIGHMEM`, where features lack robust large-folio/page-loop coverage.
- The helper asserts the caller already validated power-of-two and min/max bounds.

## Exclusive Operations
Functions serialize operations such as balance, device add/remove, device replace, resize, and swap activation:
- `btrfs_exclop_start()` starts an operation only from `BTRFS_EXCLOP_NONE`.
- `btrfs_exclop_start_try_lock()` allows compatible overlap for same operation or device-add while balance is paused; it returns with `super_lock` held on success.
- `btrfs_exclop_start_unlock()` releases that lock.
- `btrfs_exclop_finish()` clears the operation and notifies sysfs.
- `btrfs_exclop_balance()` transitions balance between active and paused states.

## Feature Flag Mutation
- `__btrfs_set_fs_incompat()` and `__btrfs_clear_fs_incompat()` mutate superblock incompat flags under `fs_info->super_lock`.
- `__btrfs_set_fs_compat_ro()` and `__btrfs_clear_fs_compat_ro()` mutate compat-ro flags similarly.
- All flag changes set `BTRFS_FS_FEATURE_CHANGED` for later user-visible/sysfs update handling.
- These helpers are used by free-space tree creation/deletion to set or clear `FREE_SPACE_TREE` and `FREE_SPACE_TREE_VALID`.

## Concurrency
- `fs_info->super_lock` protects exclusive operation state and superblock feature flag updates.
- Read-side feature checks are generally lockless because feature flags are stable enough after mount except through these controlled mutation paths.
