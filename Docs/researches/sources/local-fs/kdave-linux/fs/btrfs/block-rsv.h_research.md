# File Research: sources/local-fs/kdave-linux/fs/btrfs/block-rsv.h

This header defines the metadata block reserve interface.

Main type:
- `enum btrfs_rsv_type` names reserve categories: global, delalloc, transaction, chunk, remap, delayed operations, delayed refs, tree-log, empty fallback, and temporary.
- `struct btrfs_block_rsv` stores `size`, `reserved`, target `space_info`, spinlock, `full`, `failfast`, compact reserve type, and qgroup reservation counters.

Important fields:
- `size` is the desired reservation size for the logical operation.
- `reserved` is the amount currently charged and available.
- `space_info` chooses which Btrfs space pool owns the reservation.
- `full` is a cached fullness indicator, intentionally exposed through a data-race-tolerant fast helper.
- `failfast` changes shortage behavior for unbounded temporary operations.
- `qgroup_rsv_size` and `qgroup_rsv_reserved` track quota-group metadata reservation separately from normal metadata reservation because qgroups account net extent usage rather than full B-tree update pessimism.

Public API:
- Initialization and allocation: `btrfs_init_block_rsv()`, `btrfs_init_metadata_block_rsv()`, `btrfs_alloc_block_rsv()`, `btrfs_free_block_rsv()`.
- Root/global setup: `btrfs_init_root_block_rsv()`, `btrfs_init_global_block_rsv()`, `btrfs_update_global_block_rsv()`, `btrfs_release_global_block_rsv()`.
- Reserve mutation: `btrfs_block_rsv_add()`, `btrfs_block_rsv_refill()`, `btrfs_block_rsv_migrate()`, `btrfs_block_rsv_use_bytes()`, `btrfs_block_rsv_add_bytes()`, `btrfs_block_rsv_release()`.
- Allocation selection: `btrfs_use_block_rsv()`.
- Space-cache support: `btrfs_check_trunc_cache_free_space()`.

Inline helpers:
- `btrfs_unuse_block_rsv()` returns a consumed block back to a reserve, then releases excess.
- `btrfs_block_rsv_full()` deliberately uses `data_race()` for a fast approximate fullness check.
- `btrfs_block_rsv_reserved()` and `btrfs_block_rsv_size()` return locked snapshots for contexts that tolerate stale values but should avoid KCSAN warnings.

The header is the shared reservation contract used by transaction, tree block allocation, inode/delalloc accounting, chunk metadata, delayed refs, and free-space-cache code.
