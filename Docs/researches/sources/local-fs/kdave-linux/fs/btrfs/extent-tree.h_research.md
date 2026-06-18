# File Research: sources/local-fs/kdave-linux/fs/btrfs/extent-tree.h

This header publishes the Btrfs extent-tree interface used by allocation, delayed refs, backref validation, tree-block lifetime, snapshot deletion, discard/trim, remapping, and reserved extent handling.

Major declarations:
- Forward declares Btrfs core structures used by extent-tree APIs without forcing broad include dependencies.
- Includes `block-group.h` and `locking.h` because exported allocation control and tree block allocation interfaces depend on block group size class and lock nesting types.
- Defines the allocation policy enum used by the allocator implementation.
- Defines `struct find_free_extent_ctl`, the large per-allocation control block consumed by `find_free_extent()` and helpers.
- Defines inline-ref validation categories with `enum btrfs_inline_ref_type`.
- Declares public extent-tree functions implemented in `extent-tree.c`.

Allocation data model:
- `enum btrfs_extent_allocation_policy` distinguishes normal clustered allocation from zoned sequential allocation.
- `struct find_free_extent_ctl` carries requested sizes (`ram_bytes`, `num_bytes`, `min_alloc_size`, `empty_size`), block group profile flags, and the current search position.
- Clustered allocation fields include `empty_cluster`, `last_ptr`, and `use_cluster`.
- Retry/search state fields include `have_caching_bg`, `orig_have_caching_bg`, `retry_uncached`, `hinted`, RAID `index`, `loop`, cache state, `max_extent_size`, and `total_free_space`.
- Special allocation context fields include `delalloc`, `for_treelog`, and `for_data_reloc`.
- Result and preference fields include `found_offset`, `hint_byte`, selected `policy`, and desired block group `size_class`.

Backref and extent metadata APIs:
- `btrfs_get_extent_inline_ref_type()` validates and classifies an inline ref in a specific data/block/any context.
- `hash_extent_data_ref()` exposes the hash used for implicit data backref keys.
- `btrfs_lookup_data_extent()` searches for an extent item at a logical address and length.
- `btrfs_lookup_extent_info()` returns delayed-ref-aware refs, flags, and owner root for an extent.
- `btrfs_get_extent_owner_root()` extracts the simple-quota owner ref from an extent item when present.
- `btrfs_cross_ref_exist()` checks whether a data extent has references other than a specified inode/offset, conservatively including delayed refs.

Delayed-ref and refcount APIs:
- `btrfs_run_delayed_refs()` drains delayed ref heads for a transaction.
- `btrfs_cleanup_ref_head_accounting()` releases csum and simple quota reservations associated with a delayed-ref head.
- `btrfs_inc_extent_ref()` queues an explicit generic ref increment.
- `btrfs_free_extent()` queues or directly handles an extent reference drop depending on ref type and tree-log status.
- `btrfs_inc_ref()` and `btrfs_dec_ref()` walk an extent buffer and queue child data/tree ref changes.
- `btrfs_set_disk_extent_flags()` queues extent item flag updates.

Allocation and reservation APIs:
- `btrfs_reserve_extent()` is the public logical allocator entry point. It returns the chosen range in a `struct btrfs_key`.
- `btrfs_free_reserved_extent()` returns an unused reservation to free space.
- `btrfs_pin_reserved_extent()` moves a reserved tree block extent to pinned state.
- `btrfs_alloc_reserved_file_extent()` queues materialization of an already reserved file extent.
- `btrfs_alloc_logged_file_extent()` materializes an extent discovered during log replay and excludes it from free space.
- `btrfs_alloc_tree_block()` reserves, initializes, locks, and returns a new metadata extent buffer.
- `btrfs_free_tree_block()` queues or completes metadata block free handling.

Commit, deletion, discard, and remap APIs:
- `btrfs_finish_extent_commit()` finalizes pinned extent ranges after transaction commit and handles removed block group cleanup.
- `btrfs_drop_snapshot()` deletes a root/snapshot tree with optional backref updates and relocation mode.
- `btrfs_drop_subtree()` drops a relocation subtree rooted at a locked node.
- `btrfs_error_unpin_extent_range()` unpins an extent range during error cleanup without returning it to free space.
- `btrfs_discard_extent()` discards or resets the physical stripes backing a logical range.
- `btrfs_trim_fs()` implements filesystem-wide FITRIM behavior.
- `btrfs_handle_fully_remapped_bgs()` and `btrfs_complete_bg_remapping()` finish block groups whose extents have been remapped away.

Interface boundaries:
- This header is not a data-structure owner for extent items themselves; on-disk item definitions come from Btrfs format/accessor headers.
- The exported allocator control struct exposes internal allocator state, so callers in this tree can trace allocation behavior, but normal external callers use `btrfs_reserve_extent()`.
- APIs consistently operate under an explicit transaction handle for persistent metadata changes, except lookup/check helpers and discard/trim routines that have separate synchronization requirements.
