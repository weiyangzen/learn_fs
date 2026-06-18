# File Research: sources/local-fs/kdave-linux/fs/btrfs/block-rsv.c

This file implements Btrfs metadata block reserves. A block reserve is a logical bucket of metadata reservation with `size`, `reserved`, `full`, type, target `space_info`, and optional qgroup reservation counters.

The opening comment is the design guide:
- Normal reserve path calls `btrfs_reserve_metadata_bytes()`, charges `space_info->bytes_may_use`, and adds bytes to a reserve.
- Use path calls `btrfs_use_block_rsv()` during tree block allocation and subtracts `nodesize` from `reserved`.
- Finish path calls `btrfs_block_rsv_release()` to shrink reserve size and free or redirect excess.
- Reserve types distinguish transaction, delayed operations, chunk, global, delalloc, delayed refs, empty fallback, tree-log, remap, and temporary unbounded operations.

Core operations:
- `block_rsv_release_bytes()` shrinks reserve size, trims excess `reserved`, optionally moves excess into a destination reserve, frees remaining may-use bytes, and reports qgroup release.
- `btrfs_block_rsv_migrate()` consumes bytes from one reserve and adds them to another.
- `btrfs_init_block_rsv()` and `btrfs_init_metadata_block_rsv()` initialize reserve objects and attach metadata `space_info`.
- `btrfs_alloc_block_rsv()` and `btrfs_free_block_rsv()` allocate/free dynamic reserve objects.
- `btrfs_block_rsv_add()` reserves metadata bytes and grows both `size` and `reserved`.
- `btrfs_block_rsv_refill()` tops up `reserved` to a requested amount without growing `size`.
- `btrfs_block_rsv_release()` redirects excess preferentially to the global reserve for delayed refs, or to delayed refs for other compatible reserves.
- `btrfs_block_rsv_use_bytes()` consumes reserved bytes and clears `full` if needed.
- `btrfs_block_rsv_add_bytes()` adds bytes directly, optionally growing `size`.

Global reserve management:
- `btrfs_update_global_block_rsv()` sizes the global reserve from root, extent, checksum, free-space, block-group, and raid-stripe tree usage, plus unlink/delayed-ref minimums, capped at 512 MiB.
- It updates `space_info->bytes_may_use` directly under `space_info->lock` and reserve lock.
- It can force chunk allocation if the global reserve size reaches the total metadata space.
- `btrfs_init_global_block_rsv()` wires filesystem reserves to system, metadata, metadata-remap, and zoned treelog sub-group space infos, then updates the global reserve.
- `btrfs_release_global_block_rsv()` drains the global reserve and warns if other global reserves still carry size or reserved bytes.

Root-to-reserve routing:
- `btrfs_init_root_block_rsv()` assigns extent/csum/free-space/block-group/raid-stripe roots to delayed refs, root/dev/quota roots to global, chunk root to chunk reserve, tree-log root to treelog reserve, remap root to remap reserve, and leaves other roots without a specific reserve.
- `get_block_rsv()` prefers the transaction reserve for shareable roots, uuid root, and csum additions, then the root reserve, then the empty reserve.

Allocation fallback behavior:
- `btrfs_use_block_rsv()` first tries the selected reserve.
- For global reserves, it may refresh sizing once.
- Tree-log allocations fail immediately on reserve failure to force fsync fallback to transaction commit.
- Non-global metadata allocations may fall back to the global reserve if compatible.
- Final fallback uses `BTRFS_RESERVE_FLUSH_EMERGENCY`.
- `failfast` reserves return immediately on shortage, supporting unbounded truncate/iput style work.

Concurrency:
- Reserve state is protected by each `block_rsv->lock`.
- Global reserve updates take `space_info->lock` and reserve lock together.
- Some fast/stale checks are allowed through helpers in the header, but mutation is locked.

This file is tightly coupled to `space-info`, transaction accounting, delayed refs, chunk metadata reservation, root initialization, and ENOSPC behavior.
