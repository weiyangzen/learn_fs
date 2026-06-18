# File Research: sources/local-fs/btrfs-linux/fs/btrfs/fs.c

## Summary
Provides shared Btrfs filesystem helpers for checksum algorithms, supported block-size validation, exclusive-operation state, and superblock feature flag updates.

## Main Responsibilities
- Define checksum algorithm sizes and names.
- Compute one-shot and incremental checksums for CRC32C, xxhash64, SHA-256, and BLAKE2b.
- Validate supported filesystem block sizes for normal and experimental builds.
- Coordinate exclusive filesystem operations such as balance, device add/remove, device replace, resize, and swap activation.
- Set and clear incompat and compat-ro feature flags in the in-memory superblock copy while marking feature state changed.

## Key APIs
- Checksum metadata: `btrfs_csum_type_size()`, `btrfs_super_csum_size()`, `btrfs_super_csum_name()`, `btrfs_get_num_csums()`.
- Checksum calculation: `btrfs_csum()`, `btrfs_csum_init()`, `btrfs_csum_update()`, `btrfs_csum_final()`.
- Block size: `btrfs_supported_blocksize()`.
- Exclusive operations: `btrfs_exclop_start()`, `btrfs_exclop_start_try_lock()`, `btrfs_exclop_start_unlock()`, `btrfs_exclop_finish()`, `btrfs_exclop_balance()`.
- Feature updates: `__btrfs_set_fs_incompat()`, `__btrfs_clear_fs_incompat()`, `__btrfs_set_fs_compat_ro()`, `__btrfs_clear_fs_compat_ro()`.

## Important Behavior
Checksum type is assumed to be validated at mount time; unsupported checksum types hit `BUG()` in checksum dispatch. CRC32C uses Btrfs' inverted CRC convention, while xxhash64, SHA-256, and BLAKE2b use their normal digest flows.

Block-size support always accepts 4 KiB, `PAGE_SIZE`, and `BTRFS_MIN_BLOCKSIZE`. Experimental builds may allow block size larger than page size, except on highmem systems where large folio content cannot always be addressed safely.

Exclusive operation state is protected by `fs_info->super_lock`. Starting an operation succeeds only from `BTRFS_EXCLOP_NONE`, except `btrfs_exclop_start_try_lock()` also permits compatible reentry for the same operation and device add while balance is paused. Finishing clears the state and notifies sysfs.

Feature flag setters and clearers double-check flags under `super_lock`, update `super_copy`, log the change, and set `BTRFS_FS_FEATURE_CHANGED`.

## State and Synchronization
`fs_info->super_lock` protects exclusive-operation state and feature flag updates in `super_copy`. The checksum helpers are stateless except for `struct btrfs_csum_ctx` passed by callers.

## Risks
The checksum dispatch depends on earlier mount-time validation. A bad checksum type reaching these helpers is treated as a kernel bug, not a recoverable error.

Exclusive-operation compatibility is intentionally narrow. Callers must choose the right start helper and must pair successful try-lock paths with `btrfs_exclop_start_unlock()` and later `btrfs_exclop_finish()`.

Feature updates modify the in-memory superblock copy; persistence depends on later superblock write/commit paths noticing `BTRFS_FS_FEATURE_CHANGED`.
