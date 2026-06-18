# File Research: sources/local-fs/kdave-linux/fs/btrfs/backref.h

Purpose: Declares Btrfs backreference walking APIs, sharedness context, inode-path containers, preliminary refs, tree-block backref iterators, and backref cache structures.

Important public concepts:
- `BTRFS_ITERATE_EXTENT_INODES_STOP`: non-error sentinel for iterator-driven early stop.
- `iterate_extent_inodes_t`: callback signature for inode/offset/length/root tuples referencing an extent.
- `struct btrfs_backref_walk_ctx`: central argument/state object for backref walks. It includes target bytenr, data offset filtering, transaction/fs info/time sequence, refs/roots ulists, cache callbacks, iterator callbacks, extent item hooks, data-ref filtering, and user context.
- `struct inode_fs_paths`: path, root, and data container for inode-to-path expansion.
- `struct btrfs_backref_share_check_ctx`: reusable cache context for repeated sharedness checks, including current/previous leaf tracking, path cache, and previous extents cache.

Public APIs:
- Allocation/free: `btrfs_alloc_backref_share_check_ctx()`, `btrfs_free_backref_share_ctx()`, `init_data_container()`, `init_ipath()`.
- Extent/root/inode queries: `extent_from_logical()`, `iterate_extent_inodes()`, `iterate_inodes_from_logical()`, `paths_from_inode()`, `btrfs_find_all_leafs()`, `btrfs_find_all_roots()`, `btrfs_is_data_extent_shared()`.
- Path/ref helpers: `btrfs_ref_to_path()`, `btrfs_find_one_extref()`, `tree_backref_for_extent()`.
- Slab lifecycle: `btrfs_prelim_ref_init()` and `btrfs_prelim_ref_exit()`.

Iterator/cache structures:
- `struct prelim_ref`: internal merged backref candidate with root id, search key, level, ref count, inode list, parent, and wanted disk byte.
- `struct btrfs_backref_iter`: commit-root metadata backref iterator state.
- `btrfs_backref_has_tree_block_info()` identifies the non-skinny metadata case where the first inline data is `btrfs_tree_block_info`.
- `struct btrfs_backref_node`, `struct btrfs_backref_edge`, and `struct btrfs_backref_cache`: bidirectional graph of tree blocks and parent/child edges, with pending/useless lists and relocation-mode behavior.

Integration: Used by fiemap/sharedness checks, logical-to-inode ioctl paths, qgroup/root discovery, relocation, extent tree code, and debug/inspection paths.

Risk notes: Callers must initialize context fields carefully, especially `fs_info`, `bytenr`, `extent_item_pos`, `time_seq`, `refs`, and `roots`. Ownership of ulists and inode lists differs between APIs and is documented in implementation comments.
