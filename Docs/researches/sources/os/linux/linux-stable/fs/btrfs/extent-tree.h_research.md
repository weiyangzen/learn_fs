# File Research: sources/os/linux/linux-stable/fs/btrfs/extent-tree.h

## Role

`extent-tree.h` is the public internal header for `extent-tree.c`. It declares the allocator control structure, inline-ref type enum, allocation policy enum, and the extent-tree APIs used by other Btrfs subsystems. It intentionally forward-declares most structures so callers do not need the full extent-tree implementation dependencies.

## Types

`enum btrfs_extent_allocation_policy` selects the allocation engine:

- `BTRFS_EXTENT_ALLOC_CLUSTERED`: regular free-space-cache based allocation, optionally using metadata/data allocation clusters.
- `BTRFS_EXTENT_ALLOC_ZONED`: sequential allocation for zoned filesystems.

`struct find_free_extent_ctl` is the state object passed through `find_free_extent()` and its helpers. Fields include:

- Basic request parameters: `ram_bytes`, `num_bytes`, `min_alloc_size`, `empty_size`, `flags`.
- Search position and hints: `search_start`, `hint_byte`, `hinted`.
- Cluster state: `empty_cluster`, `last_ptr`, `use_cluster`.
- Allocation context: `delalloc`, `for_treelog`, `for_data_reloc`.
- Cache retry state: `have_caching_bg`, `orig_have_caching_bg`, `retry_uncached`, `cached`.
- Loop/index state: RAID `index`, retry `loop`.
- Results/diagnostics: `max_extent_size`, `total_free_space`, `found_offset`.
- Policy and size-class preference: `policy`, `size_class`.

`enum btrfs_inline_ref_type` is a local validation selector for inline backrefs:

- `BTRFS_REF_TYPE_INVALID`: invalid decoded inline ref.
- `BTRFS_REF_TYPE_BLOCK`: caller requires a tree-block ref.
- `BTRFS_REF_TYPE_DATA`: caller requires a data ref.
- `BTRFS_REF_TYPE_ANY`: caller accepts either tree or data refs.

## Declared API Groups

Lookup and inline-ref helpers:

- `btrfs_get_extent_inline_ref_type()`
- `hash_extent_data_ref()`
- `btrfs_lookup_data_extent()`
- `btrfs_lookup_extent_info()`
- `btrfs_get_extent_owner_root()`
- `btrfs_cross_ref_exist()`

Delayed refs and ref accounting:

- `btrfs_run_delayed_refs()`
- `btrfs_cleanup_ref_head_accounting()`
- `btrfs_inc_extent_ref()`
- `btrfs_free_extent()`
- `btrfs_inc_ref()`
- `btrfs_dec_ref()`
- `btrfs_set_disk_extent_flags()`

Allocation, reserved extents, and tree blocks:

- `btrfs_reserve_extent()`
- `btrfs_alloc_tree_block()`
- `btrfs_free_tree_block()`
- `btrfs_alloc_reserved_file_extent()`
- `btrfs_alloc_logged_file_extent()`
- `btrfs_free_reserved_extent()`
- `btrfs_pin_reserved_extent()`
- `btrfs_pin_extent()`
- `btrfs_pin_extent_for_log_replay()`
- `btrfs_finish_extent_commit()`

Snapshot/subtree deletion:

- `btrfs_drop_snapshot()`
- `btrfs_drop_subtree()`

Discard, trim, log replay exclusion, and block-group remap:

- `btrfs_exclude_logged_extents()`
- `btrfs_error_unpin_extent_range()`
- `btrfs_discard_extent()`
- `btrfs_trim_fs()`
- `btrfs_handle_fully_remapped_bgs()`
- `btrfs_complete_bg_remapping()`

## Dependencies and Include Shape

The header includes only `<linux/types.h>`, `block-group.h`, and `locking.h`, then forward-declares Btrfs structures used in prototypes. The direct include of `block-group.h` is needed for `enum btrfs_block_group_size_class` in `find_free_extent_ctl`; `locking.h` is needed for `enum btrfs_lock_nesting` in `btrfs_alloc_tree_block()`.

## Research Notes

The header exposes a broad surface because extent-tree management is shared by tree modification, file extent allocation, transaction commit, log replay, relocation, snapshot deletion, discard, and quotas. Most callers should use the high-level APIs here rather than directly manipulating extent items or delayed refs. `find_free_extent_ctl` is declared in the header but is effectively an implementation control block for the allocator rather than a general-purpose external contract.
