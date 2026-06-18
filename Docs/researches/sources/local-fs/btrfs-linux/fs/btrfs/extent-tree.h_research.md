# File Research: sources/local-fs/btrfs-linux/fs/btrfs/extent-tree.h

Purpose:
This header declares the Btrfs extent-tree API implemented by `extent-tree.c` and exposes the allocator control structure and inline-ref type enum needed by related Btrfs subsystems.

Key includes and forward declarations:
- Includes Linux integer types plus Btrfs `block-group.h` and `locking.h`.
- Forward declares core Btrfs structures used by the API: extent buffers, free clusters, filesystem info, roots, paths, refs, disk keys, delayed ref heads/roots, and inline refs.
- Uses additional types by declaration context, including `btrfs_trans_handle`, `btrfs_inode`, `btrfs_key`, `fstrim_range`, and lock nesting enum from included Btrfs headers.

Key data structures:
- `enum btrfs_extent_allocation_policy`
  - `BTRFS_EXTENT_ALLOC_CLUSTERED`: normal free-space-cache/cluster allocator.
  - `BTRFS_EXTENT_ALLOC_ZONED`: sequential allocator for zoned filesystems.
- `struct find_free_extent_ctl`
  - Central per-allocation state passed through `find_free_extent()` and helpers.
  - Stores basic request fields: `ram_bytes`, `num_bytes`, `min_alloc_size`, `empty_size`, and allocation `flags`.
  - Stores search state: `search_start`, `hint_byte`, `found_offset`, RAID `index`, loop phase, caching status, and whether the search follows a hint.
  - Stores clustered allocation state: `empty_cluster`, `last_ptr`, `use_cluster`.
  - Stores context flags: `delalloc`, `for_treelog`, `for_data_reloc`, retry/caching booleans.
  - Stores fragmentation/availability feedback: `max_extent_size` and `total_free_space`.
  - Stores selected policy and preferred block-group size class.
- `enum btrfs_inline_ref_type`
  - Classifies inline refs as invalid, block, data, or any, for validation by inline-ref parsing.

Declared API groups:
- Inline/data ref helpers:
  - `btrfs_get_extent_inline_ref_type()` validates inline backref type in an extent buffer.
  - `hash_extent_data_ref()` computes the key hash for implicit data extent refs.
- Delayed refs and accounting:
  - `btrfs_run_delayed_refs()` processes queued delayed reference updates.
  - `btrfs_cleanup_ref_head_accounting()` releases delayed ref head reservation/accounting state.
- Lookup helpers:
  - `btrfs_lookup_data_extent()` searches for a data extent item.
  - `btrfs_lookup_extent_info()` returns ref count, flags, and owner root while considering delayed refs.
  - `btrfs_cross_ref_exist()` checks whether a data extent is cross-referenced by another owner.
  - `btrfs_get_extent_owner_root()` extracts simple-quota owner root from an extent item.
- Pinning and log replay:
  - `btrfs_pin_extent()` pins a reserved/freed range in the current transaction.
  - `btrfs_pin_extent_for_log_replay()` pins a log replay tree block and removes it from free-space cache.
  - `btrfs_exclude_logged_extents()` excludes logged extents from mixed block group free-space reuse.
  - `btrfs_error_unpin_extent_range()` unpins in error handling without restoring free space.
- Allocation/freeing:
  - `btrfs_reserve_extent()` reserves a physical extent and returns its key.
  - `btrfs_free_reserved_extent()` returns an unused reserved extent.
  - `btrfs_pin_reserved_extent()` pins a reserved tree block extent.
  - `btrfs_alloc_tree_block()` allocates and initializes a new tree block.
  - `btrfs_free_tree_block()` queues/free-handles tree block release.
  - `btrfs_alloc_reserved_file_extent()` queues insertion of a newly reserved file extent.
  - `btrfs_alloc_logged_file_extent()` records a file extent recovered from tree-log replay.
  - `btrfs_free_extent()` queues a delayed data/tree extent drop.
  - `btrfs_inc_extent_ref()` queues a delayed extent ref increment.
  - `btrfs_inc_ref()` and `btrfs_dec_ref()` update references for children of a tree block.
  - `btrfs_set_disk_extent_flags()` queues a delayed extent flag update.
- Transaction commit and cleanup:
  - `btrfs_finish_extent_commit()` unpins transaction-pinned extents and handles discard/deleted block groups.
- Snapshot/relocation:
  - `btrfs_drop_snapshot()` drops a subvolume/snapshot root.
  - `btrfs_drop_subtree()` drops a relocation subtree.
- Discard/TRIM/remap:
  - `btrfs_discard_extent()` issues discard or zone reset for a logical range.
  - `btrfs_trim_fs()` implements filesystem-wide fstrim.
  - `btrfs_handle_fully_remapped_bgs()` processes fully remapped block groups.
  - `btrfs_complete_bg_remapping()` finalizes a remapped block group.

Relationship to `extent-tree.c`:
- The header exposes only the functions and state needed by other Btrfs modules; most implementation details in `extent-tree.c` remain private static helpers.
- `find_free_extent_ctl` mirrors the internal allocator phases and is defined here because allocation tracing or nearby helpers need structured access to allocator state.
- The API forms the boundary between high-level Btrfs operations such as COW, relocation, log replay, snapshot deletion, and low-level extent-tree/block-group accounting.
