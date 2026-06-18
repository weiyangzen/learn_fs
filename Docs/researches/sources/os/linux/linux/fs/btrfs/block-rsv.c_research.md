# File Research: sources/os/linux/linux/fs/btrfs/block-rsv.c

## Scope And Role

`block-rsv.c` implements Btrfs metadata block reservations. A block reserve is a bucket of pre-reserved metadata space used by transactions, delayed allocation, delayed refs, chunk operations, remap, tree log, and global fallback paths.

The file explains the reserve model in detail: each reserve has a desired `size` and currently held `reserved` bytes. Reservations are charged to `space_info->bytes_may_use`, consumed when tree blocks are allocated, and released or migrated when operations finish.

## Reserve Model

Normal flow:

1. Reserve via `btrfs_block_rsv_add()` or `btrfs_block_rsv_refill()`.
2. Consume via `btrfs_use_block_rsv()`.
3. Finish via `btrfs_block_rsv_release()`.

Important reserve types described by the file:

- Transaction, delayed ops, and chunk reserves are scoped to specific operations.
- Global reserve is an overflow/fallback buffer for extent-tree and recovery-sensitive updates.
- Delalloc reserve is per-inode/file-extent/checksum oriented.
- Delayed refs reserve tracks delayed-reference metadata pressure and is preferentially refilled from excess.
- Empty reserve is a fallback for operations without a specific bucket.
- Temp reserve is used for unbounded truncate/iput-style operations, with `failfast` to force re-reservation loops.

## Key Functions

### Core accounting

`block_rsv_release_bytes()` is the internal release helper. It subtracts from reserve `size`, trims `reserved` down to `size`, optionally transfers excess to a destination reserve, frees remaining bytes from `space_info->bytes_may_use`, and returns qgroup metadata release amounts if requested.

`btrfs_block_rsv_add()` reserves metadata bytes from the reserve's `space_info` and adds them to both `reserved` and `size`.

`btrfs_block_rsv_refill()` reserves only the missing amount needed to reach `num_bytes`.

`btrfs_block_rsv_release()` sends excess from delayed refs to global reserve, or from most other reserves to delayed refs when possible, before freeing remaining bytes.

`btrfs_block_rsv_use_bytes()` subtracts bytes from a reserve if enough are available.

`btrfs_block_rsv_add_bytes()` adds bytes to a reserve and optionally grows `size`.

`btrfs_block_rsv_migrate()` consumes bytes from one reserve and adds them to another.

### Initialization and teardown

`btrfs_init_block_rsv()` zeroes and initializes a reserve.

`btrfs_init_metadata_block_rsv()` initializes a metadata reserve and binds it to metadata `space_info`.

`btrfs_alloc_block_rsv()` allocates a heap reserve.

`btrfs_free_block_rsv()` releases all bytes and frees the object.

`btrfs_init_root_block_rsv()` assigns each special tree root to the correct reserve:
- Extent/csum/free-space/block-group/raid-stripe roots use delayed refs reserve.
- Root/dev/quota roots use global reserve.
- Chunk root uses chunk reserve.
- Tree log uses treelog reserve.
- Remap tree uses remap reserve.
- Other roots default to no root reserve.

`btrfs_init_global_block_rsv()` binds global filesystem reserves to their correct `space_info`, with a dedicated treelog subgroup in zoned mode, then updates the global reserve.

`btrfs_release_global_block_rsv()` releases global reserve and warns if other global reserves still hold size/reserved bytes.

### Global reserve sizing

`btrfs_update_global_block_rsv()` computes global reserve size from used bytes in global roots, extent/csum/free-space roots, block-group and stripe roots when enabled, and a minimum unlink/delayed-ref safety budget. It caps size at `SZ_512M`, adjusts `space_info->bytes_may_use`, marks the reserve full if exact, and may force chunk allocation if reserve size exceeds current space.

### Reserve selection and use

`get_block_rsv()` chooses the reserve for a tree-block allocation:
- Shareable roots, uuid root, and checksum-tree updates while adding checksums use the transaction reserve.
- Otherwise root-specific reserve is used.
- If none exists, empty reserve is used.

`btrfs_use_block_rsv()` consumes a block from the selected reserve. If direct use fails, it may:
- Refresh the global reserve once.
- Try a no-flush metadata reservation.
- Refuse tree-log global fallback, forcing fsync to fall back to commit.
- Use global reserve if compatible.
- Try emergency flush reservation as a last resort.

`btrfs_check_trunc_cache_free_space()` checks whether a reserve has enough space for truncating free-space cache and updating an inode.

## Integration Points

The file depends on:
- `space-info` for metadata reservation and freeing.
- Root IDs and root item accounting.
- Transaction handles.
- Block-group and zoned-mode subgroup setup.
- Qgroup metadata reserve accounting.
- Tree-log behavior.

It is used by tree block allocation, transaction commit/update paths, delayed refs, inode updates, chunk-tree operations, and truncation/eviction code.

## Concurrency Notes

Every reserve has a spinlock protecting `size`, `reserved`, `full`, and qgroup reserve counters.

`btrfs_update_global_block_rsv()` locks both the space-info and reserve while changing reserve size and `bytes_may_use`.

`btrfs_block_rsv_full()` is intentionally a lockless/data-race-tolerant fast path defined in the header.

## Error Handling

Most public functions return `-ENOSPC` when reservation or use fails.

`btrfs_use_block_rsv()` returns `ERR_PTR(ret)` for allocation failure paths.

Tree-log allocation explicitly avoids consuming global reserve or emergency metadata, because log trees are optimizations and should fall back to full transaction commit.

## Risks And Edge Cases

The release path can move bytes into delayed refs or global reserve. Incorrect destination selection would skew metadata accounting or starve delayed refs.

`num_bytes == (u64)-1` has special meaning: release the full reserve size.

Global reserve sizing must track new global roots/features. Missing a root type can under-reserve for transaction-critical updates.

Zoned mode uses a special treelog `space_info` subgroup; non-zoned assumptions would break treelog reservation isolation.

## Testing Signals

Relevant coverage includes:
- Metadata ENOSPC and overcommit behavior.
- Delayed refs reserve refill from released bytes.
- Global reserve update after root usage changes.
- Tree-log allocation failure fallback.
- Truncate/iput temp reserve failfast behavior.
- Zoned treelog reservation subgroup handling.
- Qgroup metadata release accounting.
