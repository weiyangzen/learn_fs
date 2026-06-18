# File Research: sources/local-fs/btrfs-linux/fs/btrfs/ctree.c

## Purpose

Implements the core Btrfs copy-on-write B-tree algorithms: path allocation, tree search, root/node/leaf COW, balancing, insertion, deletion, item resizing/splitting, old-tree traversal, and traversal helpers.

## Main Responsibilities

- Manages `struct btrfs_path` allocation, release, locking, and extent-buffer references.
- Performs safe root-node lookup under RCU.
- Implements COW for tree blocks, including backref updates, relocation handling, qgroup hooks, and dirty-root tracking.
- Provides binary key search in leaves and internal nodes.
- Implements `btrfs_search_slot()` and old-tree variants.
- Balances and splits internal nodes and leaves during insert/delete.
- Inserts, deletes, truncates, extends, duplicates, and splits leaf items.
- Provides forward/backward traversal helpers.
- Initializes/destroys the path slab cache.

## Key Data And State

- `btrfs_path_cachep`: slab cache for `struct btrfs_path`.
- Tree manipulation revolves around `struct extent_buffer`, `struct btrfs_root`, `struct btrfs_path`, and transaction handles.
- Root dirty state is tracked through root state bits and `fs_info->dirty_cowonly_roots`.
- Tree modification logging is updated around root replacement, node key changes, pointer movement, and extent-buffer copies.

## Important Functions

- Path lifecycle: `btrfs_alloc_path()`, `btrfs_free_path()`, `btrfs_release_path()`.
- Root and COW: `btrfs_root_node()`, `btrfs_copy_root()`, `btrfs_block_can_be_shared()`, `btrfs_force_cow_block()`, `btrfs_cow_block()`.
- Search: `btrfs_bin_search()`, `btrfs_search_slot()`, `btrfs_search_old_slot()`, `btrfs_search_slot_for_read()`, `btrfs_find_item()`, `btrfs_search_backwards()`.
- Traversal: `btrfs_search_forward()`, `btrfs_find_next_key()`, `btrfs_next_old_leaf()`, `btrfs_next_old_item()`, `btrfs_previous_item()`, `btrfs_previous_extent_item()`.
- Internal-node balancing: `balance_level()`, `push_nodes_for_insert()`, `push_node_left()`, `balance_node_right()`, `split_node()`, `insert_new_root()`, `insert_ptr()`, `promote_child_to_root()`.
- Leaf balancing: `push_leaf_left()`, `push_leaf_right()`, `split_leaf()`, `copy_for_split()`, `push_for_double_split()`.
- Item operations: `btrfs_insert_empty_items()`, `btrfs_insert_item()`, `btrfs_setup_item_for_insert()`, `btrfs_del_items()`, `btrfs_del_ptr()`, `btrfs_split_item()`, `btrfs_duplicate_item()`, `btrfs_truncate_item()`, `btrfs_extend_item()`, `btrfs_set_item_key_safe()`.
- Init/exit: `btrfs_ctree_init()`, `btrfs_ctree_exit()`.

## Control Flow

`btrfs_search_slot()` is the central entry point. It chooses a root buffer, descends level by level, does binary search at each extent buffer, optionally COWs nodes, proactively splits for insertions, balances for deletions, reads child blocks when needed, and returns a path positioned at the target key or insertion slot. It restarts on lock upgrade, path release, setup changes, or blocking reads.

COW begins with `should_cow_block()` deciding whether a block can be modified in place in the current transaction. If COW is needed, `btrfs_force_cow_block()` allocates a new tree block, copies the old block, updates generation/owner/backref metadata, updates refs, replaces the root pointer or parent pointer, frees the old tree block when appropriate, marks buffers dirty, and updates tree-mod-log state.

Insertions use top-down preparation. Full internal nodes are split or pushed into siblings before descent. Full leaves are first pushed left/right when possible, then split, with double-split avoidance for large middle insertions. After space exists, `setup_items_for_insert()` shifts item metadata/data and installs new keys and item sizes.

Deletions remove item data, shift remaining item metadata/data, update parent low keys when slot 0 changes, and may merge or delete sparse leaves. Internal deletion balancing prevents underfull nodes and can promote a sole child to root to reduce tree height.

Old-tree and commit-root traversal uses tree modification logs and optional commit-root semaphores to provide stable historical views for send and similar users.

## Integration Points

- Extent allocation/freeing is delegated to extent-tree helpers.
- Tree IO and extent-buffer validation are delegated to disk-io and tree-checker paths.
- Locking relies on Btrfs tree locks and lock nesting classes from `locking.h`.
- Transaction correctness is enforced through running transaction and generation checks.
- Relocation and qgroup code integrate through relocation COW hooks and delayed subtree tracing.
- Tree modification log calls preserve old views for backref walking and send.
- Exported APIs are declared in `ctree.h` and used across metadata, file-item, extent, relocation, logging, and defrag paths.

## Invariants And Risks

- Key order is strict by objectid, type, offset; sibling key order is checked during merges/pushes.
- Tree modifications require appropriate write locks and transaction generation match.
- Slot 0 changes require parent key fixups through `fixup_low_keys()`.
- Shareable roots require correct backref conversion and relocation semantics.
- Several corruption paths abort the transaction with `-EUCLEAN`.
- Many helpers assume callers pass a properly locked and positioned path.
- Path release can happen internally on restart/error; callers must honor return codes and path state.
- `BUG_ON()`/`BUG()` remain in invariant violation paths, reflecting kernel-fatal assumptions.

## Testing Notes

Coverage should include insertion at beginning/middle/end, large item double splits, batch insertion, item truncation/extension from front and end, deletion that empties leaves, internal node underflow, root height growth/shrink, COW of shared and unshared roots, relocation roots, old-tree traversal, nowait read search, commit-root search, and corruption detection for bad sibling ordering.
