# File Research: sources/os/linux/linux/fs/btrfs/backref.h

Purpose: Declares Btrfs backreference walking APIs, sharedness-check state, prelim-ref state, tree-backref iteration, and backref-cache structures.

Public backref context:
- `BTRFS_ITERATE_EXTENT_INODES_STOP`: non-error sentinel for iterator-driven early stop.
- `iterate_extent_inodes_t`: callback for inode/file-offset/root references to a data extent.
- `struct btrfs_backref_walk_ctx`: top-level walk parameters and outputs, including target bytenr, data extent offset filtering, transaction, fs info, tree-mod-log sequence, refs/roots ulists, cache callbacks, iterator hooks, extent-item filter, data-ref skip callback, and user context.

Sharedness context:
- `struct btrfs_backref_share_check_ctx`: stores a temporary refs ulist, current/previous leaf bytenrs, per-level path cache, and a small previous-extents cache.
- `BTRFS_BACKREF_CTX_PREV_EXTENTS_SIZE` is 8.

Main APIs:
- Allocation/free for share-check contexts.
- `extent_from_logical()`: find the extent item containing a logical address.
- `tree_backref_for_extent()`: iterate tree refs from an extent item.
- `iterate_extent_inodes()` and `iterate_inodes_from_logical()`.
- `paths_from_inode()`, `btrfs_ref_to_path()`, and result container initialization.
- `btrfs_find_all_leafs()` and `btrfs_find_all_roots()`.
- `btrfs_find_one_extref()` and `btrfs_is_data_extent_shared()`.
- Prelim-ref slab init/exit.

Internal/prelim structures exposed for related code:
- `struct prelim_ref`: temporary ref record used during backref resolution, with root ID, search key, level, count, inode list, parent, and wanted disk bytenr.
- `struct btrfs_backref_iter`: state for iterating one extent’s tree block refs in commit root.

Backref cache structures:
- `struct btrfs_backref_node`: cached tree block node with rb/simple node linkage, current/new bytenr, owner, lists, root, extent buffer, level, and state flags such as locked, processed, checked, pending, detached, and reloc-root.
- `struct btrfs_backref_edge`: links upper and lower backref nodes.
- `struct btrfs_backref_cache`: rb tree of nodes, per-level pending lists, pending/useless edge lists, counters, fs info, and relocation mode flag.

Cache APIs:
- Init, allocate/free node/edge, unlock/drop node buffers, cleanup/drop nodes, release cache.
- `btrfs_backref_add_tree_node()`, `btrfs_backref_finish_upper_links()`, and `btrfs_backref_error_cleanup()`.
- `btrfs_backref_panic()` reports cache inconsistency as a filesystem panic.

Risk notes: The header exposes subtle ownership and state-machine structures shared with relocation code. Mismanaging node/edge linkage, extent buffer lifetime, or root references can corrupt the cache or leak/over-release metadata resources.
