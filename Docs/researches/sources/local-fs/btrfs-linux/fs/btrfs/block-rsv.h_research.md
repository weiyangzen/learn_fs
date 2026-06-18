# File Research: sources/local-fs/btrfs-linux/fs/btrfs/block-rsv.h

## Scope

This header declares the Btrfs block-reserve types, `struct btrfs_block_rsv`, core reserve management APIs, and small inline helpers for reserve fullness, reserved byte reads, size reads, and unuse behavior.

## Types And Structures

`enum btrfs_rsv_type` defines reserve categories:

- `BTRFS_BLOCK_RSV_GLOBAL`
- `BTRFS_BLOCK_RSV_DELALLOC`
- `BTRFS_BLOCK_RSV_TRANS`
- `BTRFS_BLOCK_RSV_CHUNK`
- `BTRFS_BLOCK_RSV_REMAP`
- `BTRFS_BLOCK_RSV_DELOPS`
- `BTRFS_BLOCK_RSV_DELREFS`
- `BTRFS_BLOCK_RSV_TREELOG`
- `BTRFS_BLOCK_RSV_EMPTY`
- `BTRFS_BLOCK_RSV_TEMP`

`struct btrfs_block_rsv` stores target size, reserved bytes, backing `space_info`, lock, fullness/failfast booleans, reserve type, and qgroup reservation mirrors. The qgroup fields are intentionally separate because quota groups account net metadata changes differently from the normal nodesize-based reserve model.

## Public API Surface

The header exposes initialization, allocation, free, add, check, refill, migrate, use, add-bytes, release, global reserve update/init/release, root reserve assignment, reserve selection/use for tree allocation, and truncate-cache free-space checking.

## Inline Helpers

- `btrfs_unuse_block_rsv()` returns a block to a reserve and then releases excess according to normal reserve-release policy.
- `btrfs_block_rsv_full()` is a data-race-tolerant fast path for fullness checks.
- `btrfs_block_rsv_reserved()` returns reserved bytes under lock.
- `btrfs_block_rsv_size()` returns size under lock.

## Dependencies And Consumers

The header forward-declares core Btrfs types and depends only on basic Linux types and spinlocks. It is consumed by transaction, extent allocation, inode/delalloc, block-group, tree-log, remap, delayed refs, and teardown paths.

## Risks And Invariants

- Direct field access can trigger KCSAN warnings or observe unstable values; helpers should be used where stale reads are acceptable.
- `full` is explicitly a fast-path hint, not a fully synchronized guarantee.
- Qgroup reserve counters are not equivalent to normal metadata reserve counters and must be updated with qgroup-specific semantics.
- `failfast` changes ENOSPC behavior and should be used only by callers prepared to retry bounded work.
