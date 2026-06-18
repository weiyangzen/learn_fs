# File Research: sources/os/linux/linux/fs/btrfs/ctree.c

## Purpose

Implements core Btrfs B-tree operations: path allocation, root access, copy-on-write of tree blocks, key search, historical search through tree-mod-log state, node/leaf balancing, insertion, deletion, item resizing/splitting, and forward/backward iteration.

## Main Responsibilities

- Manage `struct btrfs_path` allocation, release, locking, and extent-buffer references.
- Safely acquire current root nodes under RCU and commit-root contexts.
- Perform copy-on-write of tree blocks with correct backreference updates.
- Search B-trees with correct read/write locking and restart behavior.
- Support searches over old tree versions using the tree modification log.
- Maintain B-tree shape by splitting, pushing, balancing, and promoting nodes/leaves.
- Insert, duplicate, split, extend, truncate, and delete leaf items.
- Maintain parent low keys after modifications to slot 0.
- Iterate to next/previous leaves and items.
- Initialize and destroy the path kmem cache.

## Key State

- `static struct kmem_cache *btrfs_path_cachep`: slab cache for `struct btrfs_path`.
- B-tree structure state is mostly held in:
  - `struct btrfs_root`
  - `struct extent_buffer`
  - `struct btrfs_path`
  - transaction handles
  - tree modification log records

## Path And Root Helpers

- `btrfs_alloc_path()` allocates a zeroed path.
- `btrfs_free_path()` releases locks/references then frees the path.
- `btrfs_release_path()` unlocks all held nodes and frees all extent-buffer references.
- `btrfs_root_node()` safely references the current root node using RCU and `refcount_inc_not_zero()`.
- `add_root_to_dirty_list()` queues non-shareable dirty roots for transaction writeback, keeping the extent tree last.

## Copy-On-Write Logic

- `btrfs_copy_root()` copies a root block for snapshot/relocation root creation.
- `btrfs_block_can_be_shared()` decides whether a block may still be referenced by other trees.
- `update_ref_for_cow()` updates delayed refs/backrefs for a block being COWed, handling full backrefs, relocation roots, shared refs, and last-ref cases.
- `btrfs_force_cow_block()` always allocates a new tree block, copies contents, updates parent/root pointers, updates tree-mod-log, frees old block references, and returns the new locked buffer.
- `should_cow_block()` avoids unnecessary COW when the block was created in the current transaction, not written, not forced COW, and not relocation-sensitive.
- `btrfs_cow_block()` validates transaction state, rejects COW on deleting roots, traces qgroup subtree state, then delegates to forced COW when required.

## Search Logic

- `btrfs_comp_cpu_keys()` and `btrfs_comp_keys()` provide lexicographic Btrfs key ordering.
- `btrfs_bin_search()` binary-searches keys inside leaf or node extent buffers.
- `read_block_for_search()` reads or finds child blocks, verifies parent checks, handles readahead, releases upper locks before blocking I/O, and returns `-EAGAIN` when the search must restart.
- `setup_nodes_for_search()` prepares nodes during insert/delete searches by splitting full nodes or balancing sparse nodes.
- `btrfs_search_slot_get_root()` chooses commit root, unlocked root, read-locked root, or write-locked root depending on path flags and required write-lock level.
- `search_leaf()` searches the final leaf and may split it for insertions.
- `btrfs_search_slot()` is the central search routine. It supports:
  - read-only lookup,
  - insertion preparation,
  - deletion preparation,
  - COW searches,
  - nowait read search,
  - commit-root search,
  - partial descent via `lowest_level`,
  - lock restarts through `-EAGAIN`.

## Historical Search And Iteration

- `btrfs_search_old_slot()` searches an old version of a tree using tree-mod-log rewind state.
- `btrfs_prev_leaf()` finds the previous leaf by searching for the key just below the current leaf’s first key.
- `btrfs_search_slot_for_read()` returns nearest higher/lower items when exact match is not required.
- `btrfs_search_backwards()` searches and then walks backward if the exact key is absent.
- `btrfs_get_next_valid_item()` normalizes a path slot to a valid item, advancing leaves as needed.
- `btrfs_search_forward()` walks forward from a key while skipping nodes/leaves older than `min_trans`; used by defrag and tree logging.
- `btrfs_find_next_key()` computes the next key from a kept-lock path, with fallback re-search when upper locks were dropped.
- `btrfs_next_old_leaf()` / `btrfs_next_old_item()` advance iteration through current or historical tree state.
- `btrfs_previous_item()` walks backward until a matching item type and minimum objectid condition.
- `btrfs_previous_extent_item()` specializes backward search for extent or metadata extent items.

## Node Balancing And Splitting

- `promote_child_to_root()` reduces tree height when the root node has a single child.
- `balance_level()` handles deletion-time internal-node balancing, moving entries from siblings, deleting empty nodes, and updating parent keys.
- `push_nodes_for_insert()` tries to make room in full internal nodes by pushing entries to left or right siblings before splitting.
- `reada_for_search()` and `reada_for_balance()` issue metadata readahead during search/balance operations.
- `unlock_up()` releases upper-level locks when safe, preserving locks needed for slot-0 key propagation or caller-requested lock retention.
- `check_sibling_keys()` verifies sibling ordering across tree blocks, catching corruption not visible to single-block tree-checker validation.
- `push_node_left()` and `balance_node_right()` redistribute internal-node key pointers.
- `insert_new_root()` grows the tree by creating a new root level.
- `insert_ptr()` inserts a child pointer into an internal node.
- `split_node()` splits full internal nodes, including root growth and path correction.

## Leaf Balancing And Splitting

- `leaf_space_used()` and `btrfs_leaf_free_space()` compute used/free leaf item+data space.
- `push_leaf_right()` / `__push_leaf_right()` move items and item data from a leaf to its right sibling.
- `push_leaf_left()` / `__push_leaf_left()` move items and item data from a leaf to its left sibling.
- `copy_for_split()` copies the right half of a leaf into a new leaf and inserts the parent pointer.
- `push_for_double_split()` attempts to avoid three-leaf double splits for large middle insertions by pushing items into siblings.
- `split_leaf()` splits leaves when insertion cannot fit, including root creation, single split, empty split, and double split handling.
- `setup_leaf_for_split()` re-searches with `search_for_split` and `keep_locks` before splitting an existing item.

## Item Operations

- `btrfs_set_item_key_safe()` changes a leaf item key after verifying it remains ordered relative to neighbors; updates ancestor low keys if slot 0 changes.
- `split_item()` physically splits one leaf item into two adjacent items.
- `btrfs_split_item()` prepares space and calls `split_item()`.
- `btrfs_truncate_item()` shrinks item data from end or front, shifting data and adjusting keys for front truncation.
- `btrfs_extend_item()` grows item data in place after verifying leaf free space.
- `setup_items_for_insert()` creates room for a batch of new leaf items and initializes keys, offsets, and sizes.
- `btrfs_setup_item_for_insert()` wraps single-item insertion setup.
- `btrfs_insert_empty_items()` searches with insertion space requirements and initializes a batch.
- `btrfs_insert_item()` inserts one item and writes caller data into the leaf.
- `btrfs_duplicate_item()` duplicates an existing item under a new key in the same leaf.
- `btrfs_del_ptr()` deletes an internal-node pointer and fixes low keys or root level.
- `btrfs_del_leaf()` removes an empty leaf from its parent and frees its tree block.
- `btrfs_del_items()` removes leaf items, compacts item data, deletes empty leaves, and tries to merge sparse leaves into neighbors.

## Locking And Concurrency Notes

- Search code uses read locks for normal descent and upgrades/restarts when write locks are needed.
- Many operations deliberately release paths and restart to avoid blocking I/O or changing lock requirements while holding unsafe locks.
- Slot 0 is special because changing the lowest key in a block requires updating parent keys up the tree.
- `path->keep_locks`, `lowest_level`, `skip_locking`, `search_commit_root`, `need_commit_sem`, `nowait`, and `skip_release_on_error` materially alter search/locking behavior.
- Commit-root searches that may outlive `commit_root_sem` clone the lowest extent buffer in `finish_need_commit_sem_search()`.
- Tree-mod-log updates are paired with structural changes to support historical readers.

## Error Handling And Corruption Checks

- Transaction mismatches during COW are treated as filesystem corruption and abort the transaction.
- Missing refs, bad relocation backrefs, and sibling key order violations abort transactions with `-EUCLEAN`.
- Many impossible internal states use `BUG()`, `BUG_ON()`, or warnings after printing tree/leaf context.
- `read_block_for_search()` verifies level, generation, owner root, and first key through `btrfs_tree_parent_check`.
- `btrfs_leaf_free_space()` logs critical details if calculated free space is negative.

## Dependencies

- Transaction and block allocation/freeing from `transaction.h` and `extent-tree.h`.
- Extent-buffer I/O and locking from `extent_io.h`, `disk-io.h`, and `locking.h`.
- Tree modification log from `tree-mod-log.h`.
- Qgroup subtree tracing from `qgroup.h`.
- Relocation COW hooks from `relocation.h`.
- Accessor helpers from `accessors.h`.
- Tree checker and debug printing from `tree-checker.h` and `print-tree.h`.
