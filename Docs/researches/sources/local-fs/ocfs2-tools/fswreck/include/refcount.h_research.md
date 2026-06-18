# File Research: sources/local-fs/ocfs2-tools/fswreck/include/refcount.h

This header declares refcount tree corruption helpers.

Exports:
- `mess_up_refcount_tree_block()` for root/leaf refcount block and record corruption.
- `mess_up_refcount_tree()` for tree-level `rf_clusters` and `rf_count` corruption.

Integration notes:
- Implemented in `refcount.c`.
- Requires refcount-enabled volumes for most paths.
