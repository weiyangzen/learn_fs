# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/btree.h

Read status: complete, 249 lines.

Purpose: public interface and structural definitions for ZFS’s generic in-memory B-tree.

Key structures and APIs:
- `zfs_btree_hdr_t`, `zfs_btree_core_t`, and `zfs_btree_leaf_t` define internal node layouts.
- `zfs_btree_index_t` identifies a node/offset/before-position for search and insertion.
- `zfs_btree_t` stores root, height, element size, leaf capacity, element/node counts, bulk-load state, and comparator.
- Lifecycle APIs: `zfs_btree_init()`, `zfs_btree_fini()`, `zfs_btree_create()`, `zfs_btree_destroy()`, `zfs_btree_clear()`.
- Lookup/navigation APIs: `zfs_btree_find()`, `zfs_btree_first()`, `zfs_btree_last()`, `zfs_btree_next()`, `zfs_btree_prev()`, `zfs_btree_get()`.
- Mutation APIs: `zfs_btree_add()`, `zfs_btree_add_idx()`, `zfs_btree_remove()`, `zfs_btree_remove_idx()`.
- Cleanup/verification APIs: `zfs_btree_destroy_nodes()`, `zfs_btree_numnodes()`, `zfs_btree_verify()`.

Important implementation constraints:
- Returned element pointers and indexes are internal and invalidated by insertion, removal, and node destruction.
- Elements are stored exactly once; core nodes hold real elements, not copies of leaf elements.
- Comparator must return exactly `-1`, `0`, or `+1`.
- Supports optimized bulk in-order insertion via `bt_bulk`.

Dependencies: `zfs_context.h`.

Research notes:
- Useful for arbitrary sortable in-memory data with lower overhead than AVL in some workloads.
- Header documents invariants in detail, especially around node fullness and mutation invalidation.
