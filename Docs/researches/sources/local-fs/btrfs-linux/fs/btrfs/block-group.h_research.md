# File Research: sources/local-fs/btrfs-linux/fs/btrfs/block-group.h

## Scope

This header defines the Btrfs block-group data model, runtime state enums, chunk allocation force modes, caching-control state, inline helpers, and public block-group/chunk-management APIs implemented mostly by `block-group.c`.

## Types And Data Structures

- `enum btrfs_disk_cache_state` tracks v1 free-space-cache persistence: written, error, clear, setup.
- `enum btrfs_block_group_size_class` categorizes data-only block groups as unset, small up to 128 KiB, medium up to 8 MiB, or large.
- `enum btrfs_discard_state` models async discard phases: extents, bitmaps, reset cursor, and fully-remapped cleanup.
- `enum btrfs_chunk_alloc_enum` controls chunk allocation pressure: no force, limited, force, and force-for-extent with zoned activation behavior.
- `enum btrfs_block_group_flags` defines runtime bits such as inode reference held, removed, relocating/copying state, chunk item inserted, active zone, free-space-tree needs, new transaction block group, fully remapped, and stripe removal pending.
- `enum btrfs_caching_type` tracks free-space cache state: no cache, started, finished, error.
- `struct btrfs_caching_control` owns async caching work, wait queue, mutex, block-group pointer, progress counter, list node, and refcount.
- `struct btrfs_block_group` is the central in-memory representation for a logical chunk/block group. It stores accounting (`used`, `reserved`, `pinned`, `delalloc_bytes`, `bytes_super`, remap counters), profile/length/start, committed last values, free-space cache thresholds, locks, rb/list nodes, free-space cache controller, space-info link, dirty/cache IO lists, reservation and NOCOW atomics, discard state, swap extent count, zoned allocation fields, chunk physical map, active-zone list, and size class.

## Inline Helpers

- `btrfs_block_group_end()` returns `start + length`.
- `btrfs_is_block_group_used()` checks used, reserved, pinned, and remap bytes under the block-group lock.
- `btrfs_is_block_group_data_only()` excludes mixed data/metadata groups from data-only heuristics.
- `btrfs_block_group_available_space()` computes available bytes after used, pinned, reserved, super, and zoned-unusable space.
- Allocation-profile wrappers return data, metadata, or system profile via `btrfs_get_alloc_profile()`.
- `btrfs_block_group_done()` uses a memory barrier and tests finished/error cache states.

## Public API Surface

The header exposes APIs for block-group lookup/refcounting, NOCOW writer tracking, reservation waiting, free-space cache loading, free-space insertion, block-group removal, unused/reclaim queues, mount-time block-group reading, new block-group creation, pending phase-2 creation, read-only reference transitions, dirty block-group transaction handling, block/space accounting, chunk allocation, system chunk metadata reservation, teardown, reverse mapping, freeze/unfreeze, swap extent pinning, size-class use, and fully remapped block-group cleanup.

## Dependencies And Consumers

The header includes kernel atomic/list/rbtree/rwsem primitives, UAPI Btrfs tree definitions, and `free-space-cache.h`. It forward-declares Btrfs core types to avoid pulling in broad definitions. It is used by allocation, extent-tree, transaction, inode, relocation, scrub, discard, zoned, and swapfile paths that need block-group state or helper APIs.

## Risks And Invariants

- Most accounting fields require `bg->lock`; list membership often requires fs-wide locks or `groups_sem`.
- `bg_list` is intentionally reused across several fs and transaction lists, so callers must respect ownership and refcount rules.
- `reservations` and `nocow_writers` are waitable atomics and are part of correctness for read-only transitions.
- `frozen` prevents logical/physical reuse after deletion while transactionless trim/scrub users may still hold references.
- Zoned-only fields must not be treated as valid for regular filesystems.
- The struct encodes multiple subsystems in one object, so field ownership is split among allocator, free-space cache, transaction commit, discard, zoned, swap, and relocation code.
