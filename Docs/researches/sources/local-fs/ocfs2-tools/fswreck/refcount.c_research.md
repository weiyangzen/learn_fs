# File Research: sources/local-fs/ocfs2-tools/fswreck/refcount.c

This file creates and corrupts OCFS2 refcount trees.

Key behavior:
- `create_refcount_tree()` creates three files, allocates a new refcount root, attaches it to two files, inserts many refcounted extents in reverse order to force desired tree depth, updates refcounts to 2, and uses a third file to consume intervening clusters.
- `damage_refcount_block()` corrupts refcount block self block number, generation, parent, or signature.
- `damage_refcount_list()` corrupts refcount record-list count, used count, record cluster range, cluster collision, or empty-list state.
- `damage_refcount_record()` creates redundant/inconsistent records or invalid refcount values.
- `mess_up_refcount_tree_block()` creates both a depth-0 root-only tree and a depth-1 tree, then applies block/list/record corruption to root and/or leaf blocks as appropriate.
- `mess_up_refcount_tree()` creates a deeper tree and corrupts `rf_clusters` or `rf_count`.

Integration notes:
- Requires refcount-tree filesystem support.
- Uses assertions for expected tree layout after setup.
- Writes every touched root and leaf refcount block after corruption.
