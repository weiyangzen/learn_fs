# File Research: sources/local-fs/kdave-linux/fs/btrfs/fs.c

This file contains compact filesystem-wide helpers for checksum algorithms, supported block sizes, exclusive operation state, and feature flag mutation.

Checksum support:
- `btrfs_csums[]` maps checksum type ids to digest sizes and names for CRC32C, xxhash64, SHA-256, and BLAKE2b.
- `btrfs_csum_type_size()`, `btrfs_super_csum_size()`, `btrfs_super_csum_name()`, and `btrfs_get_num_csums()` expose validated checksum metadata.
- `btrfs_csum()` computes a one-shot checksum in the little-endian on-disk format for CRC32C/xxhash64 and raw digest output for SHA-256/BLAKE2b.
- `btrfs_csum_init()`, `btrfs_csum_update()`, and `btrfs_csum_final()` provide streaming checksum contexts through `struct btrfs_csum_ctx`.

Block-size support:
- `btrfs_supported_blocksize()` accepts 4 KiB, `PAGE_SIZE`, and `BTRFS_MIN_BLOCKSIZE`.
- With `CONFIG_BTRFS_EXPERIMENTAL`, larger block sizes can be accepted through large folio support, but highmem with block size larger than page size is rejected.
- The function asserts the caller has already validated power-of-two and min/max range constraints.

Exclusive operation control:
- `btrfs_exclop_start()` starts an exclusive filesystem operation only if none is active.
- `btrfs_exclop_start_try_lock()` lets compatible callers enter when the same operation is already active or when device add is allowed during paused balance.
- `btrfs_exclop_start_unlock()` releases the held `super_lock` from the try-lock path.
- `btrfs_exclop_finish()` resets the operation to none and notifies sysfs.
- `btrfs_exclop_balance()` transitions balance between active and paused states with assertions on valid prior state.

Feature flag mutation:
- `__btrfs_set_fs_incompat()` and `__btrfs_clear_fs_incompat()` update incompat feature bits in the super copy under `super_lock`, log the change, and mark filesystem features changed.
- `__btrfs_set_fs_compat_ro()` and `__btrfs_clear_fs_compat_ro()` do the same for compat-ro bits.
- All feature updates double-check under the lock to avoid duplicate logging or races.

Important invariants:
- Unknown checksum types are assumed impossible after mount-time validation and hit `BUG()` in checksum switches.
- Exclusive operation state is protected by `fs_info->super_lock`.
- Superblock feature flag changes set `BTRFS_FS_FEATURE_CHANGED` so other code can refresh exposed state.
