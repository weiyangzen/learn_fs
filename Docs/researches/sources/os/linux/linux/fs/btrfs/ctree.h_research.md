# File Research: sources/os/linux/linux/fs/btrfs/ctree.h

## Purpose

Declares core Btrfs tree/path/root structures and public B-tree manipulation APIs used across the filesystem.

## Main Responsibilities

- Define B-tree path state and readahead modes.
- Define root state bits and the in-memory `struct btrfs_root`.
- Provide root accessors for flags, ids, log transaction ids, and generations.
- Define argument structures for extent replacement and extent dropping.
- Define leaf/node sizing helpers.
- Declare ctree search, COW, insert, delete, split, iteration, and lifecycle functions.
- Provide cleanup macros for automatic path freeing/release.

## Key Types

- `enum` readahead modes:
  - `READA_NONE`
  - `READA_BACK`
  - `READA_FORWARD`
  - `READA_FORWARD_ALWAYS`

- `struct btrfs_path`:
  - `nodes[]`: extent buffers from leaf to root.
  - `slots[]`: selected item/pointer slot per level.
  - `locks[]`: lock mode held per level.
  - `reada`, `lowest_level`: search behavior.
  - Flags controlling split searches, lock retention, skipped locking, commit-root search, extension search, nowait, and error-release behavior.

- Root state bits:
  - transaction setup,
  - shareability,
  - dirty tracking,
  - orphan/dead/deleting states,
  - defrag running,
  - forced COW,
  - log tree state,
  - qgroup flushing,
  - relocation lockdep reset.

- `struct btrfs_root`:
  - Current root node, commit root, log root, relocation root.
  - Root item/key and filesystem pointer.
  - Log synchronization state.
  - Dirty, delayed allocation, ordered extent, relocation, qgroup, swapfile, inode, and delayed-node tracking.
  - Defrag progress keys.
  - Qgroup swapped-block tracking.
  - Debug/sanity fields under config options.

- `struct btrfs_replace_extent_info`: describes a new or cloned extent replacing a file range.
- `struct btrfs_drop_extents_args`: input/output contract for dropping extents and optionally inserting a replacement.
- `struct btrfs_file_private`: per-open-file private state.
- `struct btrfs_item_batch`: batch insertion descriptor for sorted keys and data sizes.

## Important Inline Helpers

- `btrfs_root_readonly()` and `btrfs_root_dead()` test little-endian root flags.
- `btrfs_root_id()` returns root key objectid.
- `btrfs_get/set_root_log_transid()` and `btrfs_get/set_root_last_log_commit()` use READ/WRITE_ONCE.
- `btrfs_get/set_root_last_trans()` accesses root transaction generation safely.
- `btrfs_root_origin_generation()` handles normal roots and relocation roots.
- `BTRFS_LEAF_DATA_SIZE()`, `BTRFS_MAX_ITEM_SIZE()`, `BTRFS_NODEPTRS_PER_BLOCK()`, and `BTRFS_MAX_XATTR_SIZE()` compute nodesize-dependent limits.
- `btrfs_comp_keys()` optimizes key comparison on little-endian systems by avoiding conversion.
- `btrfs_insert_empty_item()` wraps batch insertion for one key.
- `btrfs_next_leaf()` and `btrfs_next_item()` wrap current-tree iteration.
- `btrfs_is_fstree()` identifies filesystem tree objectids, excluding special and qgroup ids.
- `btrfs_is_data_reloc_root()` identifies the data relocation tree.

## Public APIs Declared

- Lifecycle:
  - `btrfs_ctree_init()`
  - `btrfs_ctree_exit()`

- Search/iteration:
  - `btrfs_bin_search()`
  - `btrfs_comp_cpu_keys()`
  - `btrfs_previous_item()`
  - `btrfs_previous_extent_item()`
  - `btrfs_find_next_key()`
  - `btrfs_search_forward()`
  - `btrfs_search_slot()`
  - `btrfs_search_old_slot()`
  - `btrfs_search_slot_for_read()`
  - `btrfs_next_old_leaf()`
  - `btrfs_next_old_item()`
  - `btrfs_search_backwards()`
  - `btrfs_get_next_valid_item()`

- Path lifecycle:
  - `btrfs_release_path()`
  - `btrfs_alloc_path()`
  - `btrfs_free_path()`
  - automatic cleanup macros using `DEFINE_FREE`.

- COW/root/block operations:
  - `btrfs_root_node()`
  - `btrfs_read_node_slot()`
  - `btrfs_cow_block()`
  - `btrfs_force_cow_block()`
  - `btrfs_copy_root()`
  - `btrfs_block_can_be_shared()`

- Item and leaf modification:
  - `btrfs_set_item_key_safe()`
  - `btrfs_del_ptr()`
  - `btrfs_extend_item()`
  - `btrfs_truncate_item()`
  - `btrfs_split_item()`
  - `btrfs_duplicate_item()`
  - `btrfs_find_item()`
  - `btrfs_del_items()`
  - `btrfs_del_item()`
  - `btrfs_setup_item_for_insert()`
  - `btrfs_insert_item()`
  - `btrfs_insert_empty_items()`
  - `btrfs_leaf_free_space()`

## Invariants And Usage Notes

- `struct btrfs_path` is central to lock ownership; callers must release paths on most exits unless ownership is transferred.
- `search_for_extension` changes insertion length semantics by excluding `sizeof(struct btrfs_item)`.
- `search_commit_root` requires `skip_locking`.
- `need_commit_sem` pairs commit-root access with `commit_root_sem` protection.
- `nowait` search is intended for read-only paths.
- Shareable roots require special COW/backref and dirty-root handling.
- Non-shareable roots use simple dirty-list tracking.
- `btrfs_for_each_slot` macro expects callers to preserve distinct return handling for `0`, `1`, and negative errno.
