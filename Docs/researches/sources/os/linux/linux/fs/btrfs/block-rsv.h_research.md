# File Research: sources/os/linux/linux/fs/btrfs/block-rsv.h

## Scope And Role

`block-rsv.h` defines the public interface for Btrfs metadata block reservations. It declares reserve types, the `struct btrfs_block_rsv` layout, reserve lifecycle/accounting APIs, and small inline helpers for lock-safe or lockless reserve inspection.

## Reserve Types

`enum btrfs_rsv_type` defines the reserve buckets:

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

These correspond to transaction metadata, delayed allocation, chunk-tree work, remap-tree work, delayed operations, delayed references, tree logging, fallback, and temporary unbounded operations.

## Main Structure

`struct btrfs_block_rsv` contains:

- `size`: target reservation size.
- `reserved`: currently reserved bytes.
- `space_info`: backing metadata/system/remap space info.
- `lock`: protects mutable fields.
- `full`: whether `reserved >= size`.
- `failfast`: return ENOSPC quickly instead of falling back.
- `type`: reserve type.
- `qgroup_rsv_size` and `qgroup_rsv_reserved`: qgroup metadata reservation equivalents.

The qgroup comment explains that qgroup metadata reservation tracks possible quota metadata needs differently from normal metadata reservations. It cares about net extent usage changes, not checksum size or exact tree block count.

## Public API

Initialization/allocation:
- `btrfs_init_block_rsv()`
- `btrfs_init_root_block_rsv()`
- `btrfs_alloc_block_rsv()`
- `btrfs_init_metadata_block_rsv()`
- `btrfs_free_block_rsv()`

Reservation accounting:
- `btrfs_block_rsv_add()`
- `btrfs_block_rsv_check()`
- `btrfs_block_rsv_refill()`
- `btrfs_block_rsv_migrate()`
- `btrfs_block_rsv_use_bytes()`
- `btrfs_block_rsv_add_bytes()`
- `btrfs_block_rsv_release()`

Global reserve:
- `btrfs_update_global_block_rsv()`
- `btrfs_init_global_block_rsv()`
- `btrfs_release_global_block_rsv()`

Use helpers:
- `btrfs_use_block_rsv()`
- `btrfs_check_trunc_cache_free_space()`
- `btrfs_unuse_block_rsv()`

`btrfs_unuse_block_rsv()` adds bytes back to a reserve without growing its size, then releases excess.

## Inline Helpers

`btrfs_block_rsv_full()` returns `rsv->full` through `data_race()` as a fast lockless path.

`btrfs_block_rsv_reserved()` locks the reserve, reads `reserved`, and unlocks. The comment says this is for contexts where stale values are acceptable but direct lockless reads would trigger KCSAN warnings.

`btrfs_block_rsv_size()` similarly returns `size` under the spinlock.

## Integration Points

This header forwards declarations for transaction handles, roots, filesystem info, space info, and reserve flush modes. It is consumed by transaction code, inode/delalloc code, delayed refs, chunk allocation, tree-log code, qgroups, and block-group accounting.

## Concurrency Notes

The reserve lock protects exact accounting fields. The header explicitly distinguishes:
- Lockless approximate/full checks through `data_race()`.
- Locked stale-tolerant reads for KCSAN cleanliness.
- Mutation through implementation functions in `block-rsv.c`.

## Risks And Edge Cases

Callers must use the correct reserve type because release behavior and fallback logic differ by type.

Direct field access can race; helper use is expected unless the caller already holds `lock`.

Qgroup reserve fields are not equivalent to normal `size/reserved`, so they should not be mechanically updated as if they represented the same resource.

## Testing Signals

Expected coverage is mostly indirect:
- ENOSPC reservation paths.
- Delalloc metadata reservation.
- Delayed ref reservation release/refill.
- Global reserve fallback.
- Tree-log reserve failure.
- Qgroup metadata reserve accounting.
