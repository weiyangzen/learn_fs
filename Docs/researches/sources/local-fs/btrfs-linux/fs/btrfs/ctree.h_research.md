# File Research: sources/local-fs/btrfs-linux/fs/btrfs/ctree.h

## Purpose

Defines the public in-memory Btrfs tree interfaces and key structures used by the core B-tree implementation and metadata users.

## Main Responsibilities

- Defines tree readahead modes and `struct btrfs_path`.
- Defines `struct btrfs_root` and root state bits.
- Declares B-tree search, traversal, COW, item mutation, insertion, and deletion APIs.
- Provides leaf/node sizing helpers.
- Provides key comparison helpers and slot iteration macros.
- Defines structures for extent replacement and extent dropping arguments.

## Key Structures

- `struct btrfs_path`: arrays of extent buffers, slots, locks, readahead mode, lowest search level, and search/locking behavior flags.
- `struct btrfs_root`: in-memory root state including active and commit roots, root item/key, log tree state, dirty/ordered/delalloc lists, inode indexes, qgroup state, relocation state, accounting, snapshot/send/dedupe counters, and root state flags.
- `struct btrfs_qgroup_swapped_blocks`: tracks swapped tree blocks for delayed qgroup subtree tracing.
- `struct btrfs_replace_extent_info`: describes a replacement or clone extent operation for file range replacement.
- `struct btrfs_drop_extents_args`: input/output contract for dropping file extents.
- `struct btrfs_file_private`: per-file private VFS state for directory fill and llseek caching.
- `struct btrfs_item_batch`: sorted keys and data sizes for batch insertion.

## Important APIs And Helpers

- Path helpers: `BTRFS_PATH_AUTO_FREE`, `BTRFS_PATH_AUTO_RELEASE`, `btrfs_alloc_path()`, `btrfs_free_path()`, `btrfs_release_path()`.
- Root helpers: `btrfs_root_readonly()`, `btrfs_root_dead()`, `btrfs_root_id()`, log transid accessors, last trans accessors, `btrfs_root_origin_generation()`.
- Sizing helpers: `BTRFS_LEAF_DATA_SIZE()`, `BTRFS_MAX_ITEM_SIZE()`, `BTRFS_NODEPTRS_PER_BLOCK()`, `BTRFS_MAX_XATTR_SIZE()`.
- Key comparison: `btrfs_comp_cpu_keys()` and endian-aware `btrfs_comp_keys()`.
- Tree APIs: `btrfs_search_slot()`, `btrfs_search_old_slot()`, `btrfs_search_forward()`, `btrfs_find_next_key()`, `btrfs_next_old_leaf()`, `btrfs_next_old_item()`.
- Mutation APIs: `btrfs_cow_block()`, `btrfs_force_cow_block()`, `btrfs_copy_root()`, `btrfs_set_item_key_safe()`, `btrfs_extend_item()`, `btrfs_truncate_item()`, `btrfs_split_item()`, `btrfs_duplicate_item()`, `btrfs_insert_empty_items()`, `btrfs_insert_item()`, `btrfs_del_items()`.
- Iteration macro: `btrfs_for_each_slot()` wraps search and next-valid-item iteration.

## Integration Points

This header is a central dependency for Btrfs metadata code. It connects disk-format definitions from `uapi/linux/btrfs_tree.h`, locking/accessor helpers, transaction-aware tree mutation, file extent manipulation, relocation, logging, qgroup, defrag, and VFS-facing code.

## Invariants And Risks

- `struct btrfs_path` lock flags must mirror the actual locks held on `nodes[]`.
- `search_commit_root` requires `skip_locking` according to implementation assertions.
- Root state bits encode important mutually significant behavior, especially `BTRFS_ROOT_SHAREABLE` versus dirty tracking.
- Key comparison must match on-disk ordering; little-endian builds optimize by casting disk keys to CPU keys.
- Batch insert callers must pass sorted keys and correct aggregate data size.

## Testing Notes

Header-level validation is mostly compile and integration coverage. Important users should test automatic path cleanup, root state transitions, search flags, item batch insertion, iteration macro behavior, and endian-independent key ordering.
