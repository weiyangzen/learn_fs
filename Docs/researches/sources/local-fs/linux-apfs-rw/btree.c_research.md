# File Research: sources/local-fs/linux-apfs-rw/btree.c

This file implements APFS b-tree query and update operations plus object-map lookup/update support. It is copy-on-write aware and is used by catalog, omap, free queue, extent-reference, sealed fext, snapshot, and other trees.

Object-map support:
- Maintains a small direct-mapped omap cache keyed by oid.
- Resolves virtual object ids to physical block numbers for mounted xid or newest xid.
- Handles snapshot-aware CoW: if writing an object whose omap record belongs to a snapshot, it inserts a new omap record for the current xid; otherwise it replaces the existing mapping.
- Provides `apfs_create_omap_rec()` and `apfs_delete_omap_rec()` for object lifecycle updates.

Query support:
- `apfs_alloc_query()` creates query-chain nodes and inherits key/flags from parents.
- `apfs_free_query()` releases the chain and non-root nodes.
- `apfs_btree_query()` descends from root to leaf, using `apfs_node_query()` at each level, `apfs_child_from_query()` to read child ids, and a depth cap of 12 to reject corrupt trees.
- It supports reverse/forward multiple-record traversal, exact matches, and insertion-before-first positioning.
- `apfs_query_direct_forward()` flips a successful query chain into forward listing mode.

Mutation support:
- `apfs_query_join_transaction()` CoWs non-root nodes into the current transaction and updates parent physical child pointers when needed.
- `apfs_btree_insert()` wraps `__apfs_btree_insert()` with retry after node split and refreshes invalidated query ancestors.
- `apfs_btree_remove()` removes leaf records, recursively removes empty child nodes, updates parent first keys, and changes root leaf status if the tree empties.
- `apfs_btree_replace()` replaces key/value material without changing ordering and retries after splits.
- Root b-tree metadata is updated for record count, node count, longest key, and longest value.

Integrity checks include validation of nonleaf child value length, sealed catalog index value length, max tree depth, expected leaf/root state, and stale record clearing on failed queries.

Research relevance: this is the generic metadata-tree engine. Most higher-level APFS changes depend on its query-chain refresh, transaction joining, node splitting, and root counter maintenance.
