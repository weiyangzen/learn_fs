# File Research: sources/os/linux/linux-stable/fs/hfs/bnode.c

## Scope

This file implements basic HFS B-tree node I/O, validation, cache/hash management, reference counting, creation, unlinking, and deletion cleanup.

## Public And Internal APIs Covered

- Bounds helpers: `is_bnode_offset_valid()`, `check_and_correct_requested_length()`.
- Node data access: `hfs_bnode_read()`, `hfs_bnode_read_u16()`, `hfs_bnode_read_u8()`, `hfs_bnode_read_key()`, `hfs_bnode_write()`, `hfs_bnode_write_u16()`, `hfs_bnode_write_u8()`, `hfs_bnode_clear()`, `hfs_bnode_copy()`, `hfs_bnode_move()`.
- Diagnostics/linking: `hfs_bnode_dump()`, `hfs_bnode_unlink()`.
- Cache/lifecycle: `hfs_bnode_findhash()`, `hfs_bnode_unhash()`, `hfs_bnode_find()`, `hfs_bnode_create()`, `hfs_bnode_get()`, `hfs_bnode_put()`, `hfs_bnode_free()`.

## Control Flow And Behavior

All explicit node offset operations first validate that the starting offset is within `tree->node_size`; overlong requests are truncated with an error log. Reads can span pages in `node->page[]`, honoring `page_offset` and `pages_per_bnode`. Writes, clears, copies, and moves operate on mapped page data and mark destination pages dirty. Key reads use variable key length for leaf or variable-index-key trees, otherwise fixed maximum key length, and reject impossible key lengths by zeroing the destination key.

`hfs_bnode_unlink()` updates previous and next sibling descriptors, adjusts tree leaf head/tail for leaf nodes, clears the tree root/depth if unlinking the root, and marks the node deleted. Actual bitmap freeing is deferred until the final `hfs_bnode_put()`.

The node cache is a hash table keyed by node id. `__hfs_bnode_create()` allocates a variable-sized `hfs_bnode`, inserts it into the hash under `hash_lock` unless another thread won the race, initializes refcount/waitqueue, reads the node's pages from the B-tree inode mapping, and leaves `HFS_BNODE_NEW` set until validation completes. Racing finders wait on `lock_wq` for `HFS_BNODE_NEW` to clear.

`hfs_bnode_find()` first checks the hash, otherwise creates a node, reads the descriptor, validates node type/height against tree depth, validates record offset table monotonicity/range/alignment, and validates index/leaf key sizes against entry sizes. On success it clears `HFS_BNODE_NEW` and wakes waiters. On failure it sets `HFS_BNODE_ERROR`, wakes waiters, drops the node, and returns `-EIO`.

`hfs_bnode_create()` creates a new zeroed node, dirties all pages covering it, clears the new flag, and wakes waiters. `hfs_bnode_put()` decrements the refcount under the tree hash lock; final deleted nodes are unhashed, cleared on disk, released from the B-tree node bitmap with `hfs_bmap_free()`, and freed.

## State And Data Structures

Nodes track tree pointer, node id, flags (`HFS_BNODE_NEW`, `ERROR`, `DELETED`), refcount, waitqueue, sibling ids, parent id, node type/height, record count, page offset, page array, and hash linkage. Trees provide node size/count, depth, pages-per-node, inode mapping, hash table, and leaf head/tail.

## Dependencies

The file depends on Linux page cache APIs, page copying/zeroing/mapping helpers, HFS B-tree record layout, B-tree bitmap freeing, hash locking, and node flags.

## Risks And Invariants

Offset correction prevents out-of-bounds memory access but can mask higher-level corrupt length calculations after logging. Multi-page reads are supported, but several mutation helpers operate on `page[0]` and rely on node sizes/page offsets used by HFS. Node validation must complete before waiters use a new node. Deleted nodes are only physically freed when their refcount reaches zero, preserving cache safety during B-tree modifications.
