# File Research: sources/os/linux/linux/fs/btrfs/extent-tree.h

## Purpose

`extent-tree.h` declares the public interface and allocator control structures for Btrfs extent-tree logic implemented in `extent-tree.c`.

It exposes extent lookup, delayed-ref processing, allocation, freeing, pinning, tree-block allocation, snapshot/subtree drop, discard/trim, and block-group remapping helpers to the rest of Btrfs.

## Types

`enum btrfs_extent_allocation_policy` selects allocator behavior:
- `BTRFS_EXTENT_ALLOC_CLUSTERED`: normal allocator using free-space clusters and direct free-space searches.
- `BTRFS_EXTENT_ALLOC_ZONED`: sequential allocator for zoned filesystems.

`struct find_free_extent_ctl` carries one extent allocation attempt through `find_free_extent()`:
- Requested size/accounting fields: `ram_bytes`, `num_bytes`, `min_alloc_size`, `empty_size`, `flags`.
- Search state: `search_start`, `hint_byte`, `index`, `loop`, `cached`, `hinted`.
- Clustered allocation state: `empty_cluster`, `last_ptr`, `use_cluster`.
- Mode flags: `delalloc`, `for_treelog`, `for_data_reloc`.
- Caching/retry flags: `have_caching_bg`, `orig_have_caching_bg`, `retry_uncached`.
- Fragmentation reporting: `max_extent_size`, `total_free_space`, `found_offset`.
- Policy and preferred block-group size class: `policy`, `size_class`.

`enum btrfs_inline_ref_type` describes validation expectations when decoding an inline extent ref:
- `BTRFS_REF_TYPE_INVALID`
- `BTRFS_REF_TYPE_BLOCK`
- `BTRFS_REF_TYPE_DATA`
- `BTRFS_REF_TYPE_ANY`

The header forward-declares Btrfs and extent structures needed by prototypes without pulling in full definitions.

## Public Interface

Backref and lookup helpers:
- `btrfs_get_extent_inline_ref_type()`
- `hash_extent_data_ref()`
- `btrfs_lookup_data_extent()`
- `btrfs_lookup_extent_info()`
- `btrfs_get_extent_owner_root()`
- `btrfs_cross_ref_exist()`

Delayed refs and ref modification:
- `btrfs_run_delayed_refs()`
- `btrfs_cleanup_ref_head_accounting()`
- `btrfs_inc_extent_ref()`
- `btrfs_free_extent()`
- `btrfs_inc_ref()`
- `btrfs_dec_ref()`
- `btrfs_set_disk_extent_flags()`

Allocation and reservation:
- `btrfs_reserve_extent()`
- `btrfs_alloc_tree_block()`
- `btrfs_alloc_reserved_file_extent()`
- `btrfs_alloc_logged_file_extent()`
- `btrfs_free_reserved_extent()`

Pinning and transaction completion:
- `btrfs_pin_extent()`
- `btrfs_pin_extent_for_log_replay()`
- `btrfs_pin_reserved_extent()`
- `btrfs_finish_extent_commit()`
- `btrfs_error_unpin_extent_range()`

Tree deletion:
- `btrfs_free_tree_block()`
- `btrfs_drop_snapshot()`
- `btrfs_drop_subtree()`

Log replay/free-space exclusion:
- `btrfs_exclude_logged_extents()`

Discard, trim, and remapping:
- `btrfs_discard_extent()`
- `btrfs_trim_fs()`
- `btrfs_handle_fully_remapped_bgs()`
- `btrfs_complete_bg_remapping()`

## Role in the Module

The header defines the contract between Btrfs extent-tree internals and callers in tree modification, file extent allocation, transaction commit, tree logging/replay, relocation, qgroup accounting, and maintenance operations. Its exported API is broad because extent-tree state is central to allocation correctness, copy-on-write reference accounting, and transaction lifecycle cleanup.
